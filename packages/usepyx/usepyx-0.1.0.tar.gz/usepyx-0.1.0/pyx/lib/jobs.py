"""
PyX Background Jobs
Simple background task queue for async operations.
"""
import asyncio
import threading
from typing import Callable, Any, Optional
from datetime import datetime, timedelta
from queue import Queue
import time
import traceback


class Job:
    """Represents a background job"""
    def __init__(
        self,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        delay: float = 0,
        name: str = None
    ):
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.delay = delay
        self.name = name or func.__name__
        self.created_at = datetime.now()
        self.scheduled_at = datetime.now() + timedelta(seconds=delay)
        self.status = "pending"  # pending, running, completed, failed
        self.result = None
        self.error = None


class BackgroundWorker:
    """
    Simple background job worker.
    
    Usage:
        from pyx.jobs import jobs
        
        # Start the worker
        jobs.start()
        
        # Add a job
        @jobs.task
        def send_email(to, subject, body):
            # This runs in background
            ...
        
        # Run the task
        send_email.delay("user@example.com", "Hello", "World")
        
        # Or schedule for later
        send_email.schedule(60, "user@example.com", "Hello", "World")  # Run after 60 seconds
    """
    
    def __init__(self):
        self._queue = Queue()
        self._scheduled = []
        self._running = False
        self._thread = None
        self._completed_jobs = []
        self._failed_jobs = []
    
    def start(self):
        """Start the background worker"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()
        print("[PyX Jobs] Background worker started")
    
    def stop(self):
        """Stop the background worker"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("[PyX Jobs] Background worker stopped")
    
    def _worker_loop(self):
        """Main worker loop"""
        while self._running:
            # Check scheduled jobs
            now = datetime.now()
            ready_jobs = [j for j in self._scheduled if j.scheduled_at <= now]
            for job in ready_jobs:
                self._scheduled.remove(job)
                self._queue.put(job)
            
            # Process queue
            if not self._queue.empty():
                job = self._queue.get()
                self._execute_job(job)
            else:
                time.sleep(0.1)  # Prevent CPU spinning
    
    def _execute_job(self, job: Job):
        """Execute a single job"""
        job.status = "running"
        print(f"[PyX Jobs] Running: {job.name}")
        
        try:
            # Check if function is async
            if asyncio.iscoroutinefunction(job.func):
                # Run async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                job.result = loop.run_until_complete(job.func(*job.args, **job.kwargs))
                loop.close()
            else:
                job.result = job.func(*job.args, **job.kwargs)
            
            job.status = "completed"
            self._completed_jobs.append(job)
            print(f"[PyX Jobs] Completed: {job.name}")
            
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            self._failed_jobs.append(job)
            print(f"[PyX Jobs] Failed: {job.name} - {str(e)}")
            traceback.print_exc()
    
    def add(self, func: Callable, *args, delay: float = 0, **kwargs) -> Job:
        """
        Add a job to the queue.
        
        Args:
            func: Function to execute
            *args: Function arguments
            delay: Seconds to wait before execution
            **kwargs: Function keyword arguments
        """
        job = Job(func, args, kwargs, delay)
        
        if delay > 0:
            self._scheduled.append(job)
            print(f"[PyX Jobs] Scheduled: {job.name} in {delay}s")
        else:
            self._queue.put(job)
            print(f"[PyX Jobs] Queued: {job.name}")
        
        return job
    
    def task(self, func: Callable) -> "TaskWrapper":
        """
        Decorator to create a background task.
        
        Usage:
            @jobs.task
            def my_task(arg1, arg2):
                ...
            
            # Run in background
            my_task.delay(arg1, arg2)
            
            # Schedule for later
            my_task.schedule(60, arg1, arg2)
        """
        return TaskWrapper(self, func)
    
    def get_stats(self) -> dict:
        """Get worker statistics"""
        return {
            "running": self._running,
            "pending": self._queue.qsize(),
            "scheduled": len(self._scheduled),
            "completed": len(self._completed_jobs),
            "failed": len(self._failed_jobs)
        }
    
    def clear_history(self):
        """Clear completed and failed job history"""
        self._completed_jobs.clear()
        self._failed_jobs.clear()


class TaskWrapper:
    """Wrapper for task functions with delay/schedule methods"""
    
    def __init__(self, worker: BackgroundWorker, func: Callable):
        self.worker = worker
        self.func = func
        self.__name__ = func.__name__
    
    def __call__(self, *args, **kwargs):
        """Run synchronously"""
        return self.func(*args, **kwargs)
    
    def delay(self, *args, **kwargs) -> Job:
        """Run in background immediately"""
        return self.worker.add(self.func, *args, **kwargs)
    
    def schedule(self, delay: float, *args, **kwargs) -> Job:
        """Schedule to run after delay seconds"""
        return self.worker.add(self.func, *args, delay=delay, **kwargs)


# Global instance
jobs = BackgroundWorker()
