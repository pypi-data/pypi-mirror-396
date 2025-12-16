"""
Comprehensive Maya Persistent Server Test Suite

This test suite validates:
1. Server startup and initialization
2. Basic command execution performance
3. Concurrent request handling
4. Error handling and recovery
5. Session management
6. Real-world workflow simulation
7. Stability under load
"""

import time
import subprocess
import requests
import threading
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

MAYA_SERVER_PORT = 8766
MAYA_SERVER_URL = f"http://127.0.0.1:{MAYA_SERVER_PORT}"

class MayaPersistentServerTester:
    """Comprehensive test suite for Maya Persistent Server."""

    def __init__(self):
        self.maya_process = None
        self.test_results = {}

    def start_server(self):
        """Start Maya persistent server."""
        print("\n" + "="*60)
        print("Starting Maya Persistent Server")
        print("="*60)

        mayapy_path = r"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe"
        script_path = "maya_persistent_server_optimized.py"

        startup_start = time.time()

        self.maya_process = subprocess.Popen(
            [mayapy_path, script_path, "--port", str(MAYA_SERVER_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Monitor output in separate thread
        def read_output():
            for line in self.maya_process.stdout:
                print(f"   [Server] {line.rstrip()}")

        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()

        # Wait for server to be ready
        print("\nWaiting for server to initialize...")
        max_wait = 30
        wait_start = time.time()

        while time.time() - wait_start < max_wait:
            try:
                # Try connecting to health endpoint
                response = requests.get(f"{MAYA_SERVER_URL}/health", timeout=1)
                if response.status_code == 200:
                    data = response.json()
                    startup_time = time.time() - startup_start
                    print(f"✓ Server ready in {startup_time:.2f}s")
                    print(f"  Maya Version: {data.get('maya_version')}")
                    print(f"  Status: {data.get('status')}")
                    self.test_results['startup_time'] = startup_time
                    return True
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                time.sleep(0.5)
                continue
            except Exception as e:
                print(f"  Error during health check: {e}")
                time.sleep(0.5)
                continue

        print("✗ Server failed to start within 30 seconds")
        return False

    def test_basic_commands(self):
        """Test 1: Basic command execution."""
        print("\n" + "="*60)
        print("TEST 1: Basic Command Execution")
        print("="*60)

        commands = [
            ("Create Sphere", "cmds.polySphere(name='test_sphere')"),
            ("Create Cube", "cmds.polyCube(name='test_cube')"),
            ("Create Plane", "cmds.polyPlane(name='test_plane')"),
            ("List Objects", "result = cmds.ls(assemblies=True)"),
            ("Get Scene Name", "result = cmds.file(q=True, sceneName=True)"),
        ]

        times = []
        successes = 0

        for name, command in commands:
            try:
                start = time.time()
                response = requests.post(
                    f"{MAYA_SERVER_URL}/",
                    json={'command': command, 'operation_type': name},
                    timeout=5
                )
                elapsed = time.time() - start

                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        successes += 1
                        times.append(elapsed)
                        print(f"  ✓ {name:20} {elapsed*1000:6.1f}ms")
                    else:
                        print(f"  ✗ {name:20} Failed: {result.get('error')}")
                else:
                    print(f"  ✗ {name:20} HTTP {response.status_code}")

            except Exception as e:
                print(f"  ✗ {name:20} Exception: {e}")

        if times:
            avg_time = sum(times) / len(times)
            self.test_results['basic_commands'] = {
                'avg_time_ms': avg_time * 1000,
                'success_rate': successes / len(commands),
                'total_tests': len(commands)
            }

            print(f"\n  Results: {successes}/{len(commands)} passed")
            print(f"  Average time: {avg_time*1000:.1f}ms")

        return successes == len(commands)

    def test_concurrent_requests(self):
        """Test 2: Concurrent request handling."""
        print("\n" + "="*60)
        print("TEST 2: Concurrent Request Handling")
        print("="*60)

        num_concurrent = 10
        print(f"  Sending {num_concurrent} concurrent requests...")

        def send_request(index):
            """Send a single request."""
            try:
                start = time.time()
                response = requests.post(
                    f"{MAYA_SERVER_URL}/",
                    json={
                        'command': f"cmds.polySphere(name='concurrent_sphere_{index}')",
                        'operation_type': f'concurrent_test_{index}'
                    },
                    timeout=10
                )
                elapsed = time.time() - start

                if response.status_code == 200:
                    result = response.json()
                    return {
                        'index': index,
                        'success': result.get('success'),
                        'time': elapsed,
                        'error': result.get('error')
                    }
                else:
                    return {'index': index, 'success': False, 'time': elapsed}
            except Exception as e:
                return {'index': index, 'success': False, 'error': str(e)}

        start_time = time.time()
        results = []

        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(send_request, i) for i in range(num_concurrent)]

            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                status = "✓" if result.get('success') else "✗"
                print(f"    {status} Request {result['index']:2d}: {result.get('time', 0)*1000:6.1f}ms")

        total_time = time.time() - start_time
        successes = sum(1 for r in results if r.get('success'))
        times = [r['time'] for r in results if 'time' in r]

        if times:
            avg_time = sum(times) / len(times)
            self.test_results['concurrent_requests'] = {
                'total_requests': num_concurrent,
                'successes': successes,
                'total_time_s': total_time,
                'avg_time_ms': avg_time * 1000,
                'max_time_ms': max(times) * 1000
            }

            print(f"\n  Results: {successes}/{num_concurrent} passed")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Average time: {avg_time*1000:.1f}ms")
            print(f"  Requests/second: {num_concurrent/total_time:.1f}")

        return successes == num_concurrent

    def test_error_handling(self):
        """Test 3: Error handling and recovery."""
        print("\n" + "="*60)
        print("TEST 3: Error Handling & Recovery")
        print("="*60)

        error_tests = [
            ("Invalid Python", "this is not valid python code", False),
            ("Invalid Maya Command", "cmds.nonexistentCommand()", False),
            ("Syntax Error", "cmds.polySphere(name=", False),
            ("Valid After Error", "cmds.polyCube(name='recovery_cube')", True),
        ]

        successes = 0

        for name, command, should_succeed in error_tests:
            try:
                response = requests.post(
                    f"{MAYA_SERVER_URL}/",
                    json={'command': command, 'operation_type': name},
                    timeout=5
                )

                if response.status_code == 200:
                    result = response.json()
                    actual_success = result.get('success')

                    if actual_success == should_succeed:
                        successes += 1
                        status = "✓" if should_succeed else "✓ (expected error)"
                        print(f"  {status} {name:25} {result.get('error', 'OK')[:40]}")
                    else:
                        print(f"  ✗ {name:25} Unexpected result")
                else:
                    print(f"  ✗ {name:25} HTTP {response.status_code}")

            except Exception as e:
                print(f"  ✗ {name:25} Exception: {e}")

        self.test_results['error_handling'] = {
            'passed': successes,
            'total': len(error_tests)
        }

        print(f"\n  Results: {successes}/{len(error_tests)} passed")
        return successes == len(error_tests)

    def test_real_workflow(self):
        """Test 4: Simulate real Maya workflow."""
        print("\n" + "="*60)
        print("TEST 4: Real Workflow Simulation")
        print("="*60)

        workflow_steps = [
            ("New Scene", "cmds.file(new=True, force=True)"),
            ("Create Base Sphere", "cmds.polySphere(name='base_sphere', radius=2)"),
            ("Create Material", "shader = cmds.shadingNode('lambert', asShader=True, name='my_material')"),
            ("Assign Material", "cmds.select('base_sphere'); cmds.hyperShade(assign='my_material')"),
            ("Duplicate Objects", "for i in range(5): cmds.duplicate('base_sphere', name=f'sphere_{i}')"),
            ("Move Objects", "for i, obj in enumerate(cmds.ls('sphere_*')): cmds.move(i*3, 0, 0, obj)"),
            ("Group Objects", "cmds.group('sphere_*', name='sphere_group')"),
            ("Get Object Count", "result = len(cmds.ls(assemblies=True))"),
        ]

        workflow_start = time.time()
        successes = 0
        step_times = []

        for name, command in workflow_steps:
            try:
                start = time.time()
                response = requests.post(
                    f"{MAYA_SERVER_URL}/",
                    json={'command': command, 'operation_type': name},
                    timeout=10
                )
                elapsed = time.time() - start
                step_times.append(elapsed)

                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        successes += 1
                        print(f"  ✓ {name:25} {elapsed*1000:6.1f}ms")
                    else:
                        print(f"  ✗ {name:25} {result.get('error')}")
                else:
                    print(f"  ✗ {name:25} HTTP {response.status_code}")

            except Exception as e:
                print(f"  ✗ {name:25} Exception: {e}")

        workflow_time = time.time() - workflow_start

        if step_times:
            self.test_results['real_workflow'] = {
                'steps': len(workflow_steps),
                'successes': successes,
                'total_time_s': workflow_time,
                'avg_step_ms': (sum(step_times) / len(step_times)) * 1000
            }

            print(f"\n  Results: {successes}/{len(workflow_steps)} steps passed")
            print(f"  Total workflow time: {workflow_time:.2f}s")
            print(f"  Average step time: {sum(step_times)/len(step_times)*1000:.1f}ms")

        return successes == len(workflow_steps)

    def test_performance_stability(self):
        """Test 5: Performance stability over multiple operations."""
        print("\n" + "="*60)
        print("TEST 5: Performance Stability (50 operations)")
        print("="*60)

        num_operations = 50
        times = []
        failures = 0

        print(f"  Executing {num_operations} operations...")

        for i in range(num_operations):
            try:
                start = time.time()
                response = requests.post(
                    f"{MAYA_SERVER_URL}/",
                    json={
                        'command': f"cmds.polySphere(name='stability_test_{i}')",
                        'operation_type': f'stability_{i}'
                    },
                    timeout=5
                )
                elapsed = time.time() - start

                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        times.append(elapsed)
                    else:
                        failures += 1
                else:
                    failures += 1

                # Progress indicator
                if (i + 1) % 10 == 0:
                    print(f"    Progress: {i+1}/{num_operations} ({len(times)} successful)")

            except Exception as e:
                failures += 1

        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            variance = max_time - min_time

            self.test_results['stability'] = {
                'total_operations': num_operations,
                'successes': len(times),
                'failures': failures,
                'avg_time_ms': avg_time * 1000,
                'min_time_ms': min_time * 1000,
                'max_time_ms': max_time * 1000,
                'variance_ms': variance * 1000
            }

            print(f"\n  Results: {len(times)}/{num_operations} successful")
            print(f"  Average time: {avg_time*1000:.1f}ms")
            print(f"  Min time: {min_time*1000:.1f}ms")
            print(f"  Max time: {max_time*1000:.1f}ms")
            print(f"  Variance: {variance*1000:.1f}ms")

        return failures == 0

    def print_summary(self):
        """Print test summary and verdict."""
        print("\n" + "="*60)
        print("COMPREHENSIVE TEST SUMMARY")
        print("="*60)

        if 'startup_time' in self.test_results:
            print(f"\n📊 Startup Performance:")
            print(f"  Server initialization: {self.test_results['startup_time']:.2f}s")

        if 'basic_commands' in self.test_results:
            bc = self.test_results['basic_commands']
            print(f"\n📊 Basic Commands:")
            print(f"  Success rate: {bc['success_rate']*100:.0f}%")
            print(f"  Average time: {bc['avg_time_ms']:.1f}ms")

        if 'concurrent_requests' in self.test_results:
            cr = self.test_results['concurrent_requests']
            print(f"\n📊 Concurrent Handling:")
            print(f"  {cr['total_requests']} requests in {cr['total_time_s']:.2f}s")
            print(f"  Average time: {cr['avg_time_ms']:.1f}ms")
            print(f"  Max time: {cr['max_time_ms']:.1f}ms")

        if 'real_workflow' in self.test_results:
            rw = self.test_results['real_workflow']
            print(f"\n📊 Real Workflow:")
            print(f"  {rw['successes']}/{rw['steps']} steps completed")
            print(f"  Total time: {rw['total_time_s']:.2f}s")
            print(f"  Avg step time: {rw['avg_step_ms']:.1f}ms")

        if 'stability' in self.test_results:
            st = self.test_results['stability']
            print(f"\n📊 Stability Test:")
            print(f"  {st['successes']}/{st['total_operations']} operations successful")
            print(f"  Performance variance: {st['variance_ms']:.1f}ms")

        print("\n" + "="*60)
        print("PRODUCTION READINESS ASSESSMENT")
        print("="*60)

        # Assess readiness
        is_ready = True
        reasons = []

        startup_time = self.test_results.get('startup_time', 999)
        if startup_time > 15:
            is_ready = False
            reasons.append(f"Startup too slow: {startup_time:.1f}s > 15s")

        avg_time = self.test_results.get('basic_commands', {}).get('avg_time_ms', 999)
        if avg_time > 100:
            reasons.append(f"⚠ Average command time: {avg_time:.1f}ms (target: <100ms)")
        elif avg_time > 500:
            is_ready = False
            reasons.append(f"Commands too slow: {avg_time:.1f}ms > 500ms")

        failures = self.test_results.get('stability', {}).get('failures', 999)
        if failures > 0:
            is_ready = False
            reasons.append(f"Stability issues: {failures} failures in 50 operations")

        if is_ready:
            print("\n✓✓✓ PRODUCTION READY ✓✓✓")
            print("\nThe Maya Persistent Server approach is ready for integration!")
            print("\nNext steps:")
            print("  1. Integrate into local-dcc-agent startup sequence")
            print("  2. Route all Maya operations through HTTP API")
            print("  3. Deploy to production")
            print(f"\nExpected improvement: {6000/avg_time:.0f}x faster than current approach")
        else:
            print("\n✗ NOT READY FOR PRODUCTION")
            print("\nIssues found:")
            for reason in reasons:
                print(f"  - {reason}")

        print("="*60)

    def cleanup(self):
        """Stop the Maya server."""
        print("\nStopping Maya server...")
        if self.maya_process:
            self.maya_process.terminate()
            try:
                self.maya_process.wait(timeout=5)
            except:
                self.maya_process.kill()
            print("✓ Server stopped")

    def run_all_tests(self):
        """Run complete test suite."""
        print("\n" + "="*60)
        print("MAYA PERSISTENT SERVER - COMPREHENSIVE TEST SUITE")
        print("="*60)

        try:
            # Start server
            if not self.start_server():
                print("\n✗ FAILED: Could not start server")
                return False

            # Wait a moment for server to stabilize
            time.sleep(2)

            # Run all tests
            test1 = self.test_basic_commands()
            test2 = self.test_concurrent_requests()
            test3 = self.test_error_handling()
            test4 = self.test_real_workflow()
            test5 = self.test_performance_stability()

            # Print summary
            self.print_summary()

            return all([test1, test2, test3, test4, test5])

        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")
            return False
        except Exception as e:
            print(f"\n✗ Test suite failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.cleanup()


if __name__ == "__main__":
    tester = MayaPersistentServerTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
