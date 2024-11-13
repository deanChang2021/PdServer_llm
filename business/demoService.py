


"""
这是当我们需要使用taskQueue进行任务异步处理时使用。在imageingTask中，我们调用了这个demo.
注意，这业务实现方法，只能是方法，不能是类。因为taskQueue中的Task会将数据赋到可变参数中，类的self会接收第一个参数。
"""
import logging

from conf.logger.logQueue import logQueue


async def demo(triggerId, type, *args):
    logging.info("this is a task from task queue")
    logQueue.info("收到任务队列的任务。")