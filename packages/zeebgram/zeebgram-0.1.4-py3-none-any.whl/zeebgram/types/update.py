
import zeebgram


class Update:
    def stop_propagation(self):
        raise zeebgram.StopPropagation

    def continue_propagation(self):
        raise zeebgram.ContinuePropagation
