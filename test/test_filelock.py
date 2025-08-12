# encoding: utf-8-sig

import os
import json
import tempfile
import threading
import time
import pytest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from mktotp.secrets import SecretMgr


class TestFileLock:
    """Test class for FileLock functionality in SecretMgr"""

    @pytest.fixture
    def temp_secrets_file(self):
        """Create a temporary secrets file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            test_data = {
                "secrets": [
                    {
                        "name": "test_secret1",
                        "account": "test@example.com",
                        "issuer": "TestIssuer1",
                        "secret": "JBSWY3DPEHPK3PXP"
                    }
                ],
                "version": "1.0",
                "last_update": "2025-08-08T12:34:56+09:00"
            }
            json.dump(test_data, f, indent=4, ensure_ascii=False)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        backup_path = Path(temp_path).with_suffix('.bak')
        if backup_path.exists():
            backup_path.unlink()
        lock_path = Path(temp_path).with_suffix('.lock')
        if lock_path.exists():
            lock_path.unlink()

    def test_context_manager_creates_lock_file(self, temp_secrets_file):
        """Test that using context manager creates a lock file"""
        lock_path = Path(temp_secrets_file).with_suffix('.lock')
        
        # Ensure lock file doesn't exist initially
        assert not lock_path.exists()
        
        with SecretMgr(temp_secrets_file) as mgr:
            # Lock file should exist while context is active
            assert mgr.lock is not None
            assert mgr.lock.is_locked
        
        # Lock file might still exist but should not be locked

    def test_context_manager_releases_lock(self, temp_secrets_file):
        """Test that exiting context manager releases the lock"""
        mgr = SecretMgr(temp_secrets_file)
        
        with mgr:
            assert mgr.lock is not None
            assert mgr.lock.is_locked
        
        # After exiting context, lock should be released
        assert not mgr.lock.is_locked

    def test_concurrent_access_serialization(self, temp_secrets_file):
        """Test that concurrent access is properly serialized"""
        results = []
        errors = []
        access_order = []
        
        def worker(worker_id):
            try:
                start_time = time.time()
                with SecretMgr(temp_secrets_file) as mgr:
                    mgr.load()
                    access_time = time.time()
                    access_order.append((worker_id, access_time))
                    
                    # Simulate some work
                    time.sleep(0.1)
                    
                    # Add a unique secret for this worker
                    qr_data = f"otpauth://totp/Worker{worker_id}:worker{worker_id}@example.com?secret=JBSWY3DPEHPK3PX{worker_id}&issuer=Worker{worker_id}"
                    result = mgr.register_secret(f"worker_{worker_id}", [qr_data])
                    mgr.save()
                    
                    end_time = time.time()
                    results.append({
                        'worker_id': worker_id,
                        'start_time': start_time,
                        'access_time': access_time,
                        'end_time': end_time,
                        'result': result
                    })
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Run multiple workers concurrently
        num_workers = 3
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker, i) for i in range(num_workers)]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    errors.append(('future', str(e)))
        
        # Check that no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"
        
        # Check that all workers completed successfully
        assert len(results) == num_workers
        
        # Verify that all secrets were saved
        with SecretMgr(temp_secrets_file) as mgr:
            mgr.load()
            for i in range(num_workers):
                assert f"worker_{i}" in mgr.secret_data
        
        # Verify that access was serialized (no overlapping critical sections)
        access_order.sort(key=lambda x: x[1])  # Sort by access time
        results.sort(key=lambda x: x['access_time'])
        
        for i in range(len(results) - 1):
            current_end = results[i]['end_time']
            next_start = results[i + 1]['access_time']
            # Next worker should start after current worker finishes
            # (allowing some small tolerance for timing precision)
            assert next_start >= current_end - 0.01, f"Access not properly serialized: worker {results[i]['worker_id']} ended at {current_end}, worker {results[i+1]['worker_id']} started at {next_start}"

    def test_timeout_handling(self, temp_secrets_file):
        """Test timeout handling when lock cannot be acquired"""
        # First, acquire the lock in a separate thread and hold it
        lock_holder_started = threading.Event()
        lock_holder_should_exit = threading.Event()
        
        def lock_holder():
            with SecretMgr(temp_secrets_file) as mgr:
                lock_holder_started.set()
                # Hold the lock until signaled to exit
                lock_holder_should_exit.wait(timeout=5)
        
        lock_thread = threading.Thread(target=lock_holder)
        lock_thread.start()
        
        try:
            # Wait for the lock holder to acquire the lock
            assert lock_holder_started.wait(timeout=2), "Lock holder failed to start"
            
            # Now try to acquire the lock with a short timeout
            # This should timeout since the lock is already held
            mgr = SecretMgr(temp_secrets_file)
            
            # Temporarily modify the timeout to be very short for this test
            original_timeout = 10
            short_timeout = 0.5
            
            # Create a new instance with a shorter timeout
            mgr.lock_file = Path(temp_secrets_file).with_suffix('.lock')
            mgr.lock_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            
            from filelock import FileLock, Timeout
            mgr.lock = FileLock(mgr.lock_file, timeout=short_timeout)
            
            # This should raise a Timeout exception
            with pytest.raises(Timeout):
                mgr.lock.acquire()
                
        finally:
            # Signal the lock holder to exit and wait for it
            lock_holder_should_exit.set()
            lock_thread.join(timeout=3)

    def test_multiple_processes_simulation(self, temp_secrets_file):
        """Test simulating multiple processes accessing the same file"""
        import subprocess
        import sys
        
        # Create a script that will be run as a separate process
        script_content = f"""
import sys
import time
sys.path.insert(0, r'{Path(__file__).parent.parent / "src"}')

from mktotp.secrets import SecretMgr

try:
    with SecretMgr(r'{temp_secrets_file}') as mgr:
        mgr.load()
        # Simulate some work
        time.sleep(0.1)
        qr_data = "otpauth://totp/Process:process@example.com?secret=JBSWY3DPEHPK3PXZ&issuer=Process"
        mgr.register_secret("process_secret", [qr_data])
        mgr.save()
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {{e}}")
    sys.exit(1)
"""
        
        script_path = Path(temp_secrets_file).parent / "test_script.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        try:
            # Run the script as a subprocess
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0, f"Script failed: {result.stderr}"
            assert "SUCCESS" in result.stdout
            
            # Verify that the secret was saved
            with SecretMgr(temp_secrets_file) as mgr:
                mgr.load()
                assert "process_secret" in mgr.secret_data
                
        finally:
            # Cleanup
            if script_path.exists():
                script_path.unlink()

    def test_lock_file_cleanup_on_exception(self, temp_secrets_file):
        """Test that lock is properly released even when exceptions occur"""
        mgr = SecretMgr(temp_secrets_file)
        
        try:
            with mgr:
                mgr.load()
                # Simulate an exception
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected exception
        
        # Lock should be released even after exception
        assert not mgr.lock.is_locked

    def test_destructor_lock_cleanup(self, temp_secrets_file):
        """Test that destructor properly cleans up locks"""
        mgr = SecretMgr(temp_secrets_file)
        
        with mgr:
            mgr.load()
            lock_ref = mgr.lock
        
        # Force garbage collection
        del mgr
        import gc
        gc.collect()
        
        # Lock should be released
        assert not lock_ref.is_locked
