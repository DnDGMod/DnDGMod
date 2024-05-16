class ProgressTracker:
    def __init__(self, logger, multiples=20):
        self.multiples = multiples
        self.last_step = -1
        self.logger = logger

    def print_progress(self, block_num, block_size, total_size):
        downloaded_size = block_num * block_size
        percentage = 100 * downloaded_size / total_size
        if percentage // self.multiples > self.last_step:
            self.logger.info(f"{percentage:.0f}% downloaded")
        else:
            self.logger.debug(f"{percentage:.2f}% downloaded")
        self.last_step = percentage // self.multiples

    def reset(self):
        self.last_step = -1
