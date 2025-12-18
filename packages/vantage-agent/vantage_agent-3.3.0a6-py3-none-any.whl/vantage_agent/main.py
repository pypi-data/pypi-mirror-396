"""Main module of the project for starting the agent."""

import asyncio

from loguru import logger

from vantage_agent.scheduler import init_scheduler, shut_down_scheduler
from vantage_agent.sentry import init_sentry


def main():
    """Start the agent by initiating the scheduler."""
    logger.info("Starting the Vantage Agent")
    init_sentry()

    # Create event loop for Python 3.14 compatibility
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Initialize scheduler after event loop is set but before it runs
    # APScheduler 3.11+ requires the event loop to be running when start() is called
    # So we use call_soon to schedule the initialization
    loop.call_soon(lambda: init_scheduler())

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):  # pragma: no cover
        logger.info("Shutting down the Vantage Agent")
        # Get the scheduler instance - it should be available via the module-level variable
        from vantage_agent.scheduler import scheduler

        shut_down_scheduler(scheduler)  # pragma: no cover
    finally:
        loop.close()


if __name__ == "__main__":
    main()  # pragma: no cover
