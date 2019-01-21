import torch
import torch.nn as nn
class ZoneoutRNN(nn.Module):
    def __init__(self, cell, zoneout_prob, bidrectional=True):
        super(ZoneoutRNN, self).__init__()
        self.forward_cell = cell
        self.backward_cell = cell
        self.zoneout_prob = zoneout_prob
        self.bidrectional = bidrectional

        if isinstance(cell, nn.RNNCell):
            raise TypeError("The cell is a RNNCell!")
        if not isinstance(cell, nn.RNNCellBase):
            raise TypeError("The cell is not a LSTMCell or GRUCell!")
        if isinstance(cell, nn.LSTMCell):
            if not isinstance(zoneout_prob, tuple):
                raise TypeError("The LSTM zoneout_prob must be a tuple!")
        elif isinstance(cell, nn.GRU):
            if not isinstance(zoneout_prob, float):
                raise TypeError("The LSTM zoneout_prob must be a float number!")

    @property
    def hidden_size(self):
        return self.forward_cell.hidden_size
    @property
    def input_size(self):
        return self.forward_cell.input_size

    def forward(self, input, forward_state, backward_state):
        if self.bidrectional == True:
            forward_output, forward_new_state = self.forward_cell(input, forward_state)
            backward_output, backward_new_state = self.backward_cell(input, backward_state)
            if isinstance(self.cell, nn.LSTMCell):
                forward_h, forward_c = forward_state
                forward_new_h, forward_new_c = forward_new_state

                backward_h, backward_c = backward_state
                backward_new_h, backward_new_c = backward_new_state
                zoneout_prob_c, zoneout_prob_h = self.zoneout_prob

                forward_new_h = (1 - zoneout_prob_h) * F.dropout(forward_new_h, p=hp.dropout_rate,
                                                                 training=self.training) + forward_h
                forward_new_c = (1 - zoneout_prob_c) * F.dropout(forward_new_c, p=hp.dropout_rate,
                                                                 training=self.training) + forward_c

                backward_new_h = (1 - zoneout_prob_h) * F.dropout(backward_new_h, p=hp.dropout_rate,
                                                                 training=self.training) + backward_h
                backward_new_c = (1 - zoneout_prob_c) * F.dropout(backward_new_c, p=hp.dropout_rate,
                                                                 training=self.training) + backward_c

                forward_new_state = forward_new_h, forward_new_c
                backward_new_state = backward_new_h, backward_new_c
                forward_output = forward_new_h
                backward_output = backward_new_h

            else:
                forward_h = forward_state
                forward_new_h = forward_new_state

                backward_h = backward_state
                backward_new_h = backward_new_state
                zoneout_prob_h = self.zoneout_prob

                forward_new_h = (1 - zoneout_prob_h) * F.dropout(forward_new_h, p=hp.dropout_rate,
                                                                 training=self.training) + forward_h
                backward_new_h = (1 - zoneout_prob_h) * F.dropout(backward_new_h, p=hp.dropout_rate,
                                                                  training=self.training) + backward_h

                forward_new_state = forward_new_h
                backward_new_state = backward_new_h
                forward_output = forward_new_h
                backward_output = backward_new_h
            return forward_output, backward_output, forward_new_state, backward_new_state
        else:
            forward_output, forward_new_state = self.forward_cell(input, forward_state)
            if isinstance(self.cell, nn.LSTMCell):
                forward_h, forward_c = forward_state
                forward_new_h, forward_new_c = forward_new_state

                zoneout_prob_c, zoneout_prob_h = self.zoneout_prob

                forward_new_h = (1 - zoneout_prob_h) * F.dropout(forward_new_h, p=hp.dropout_rate,
                                                                 training=self.training) + forward_h
                forward_new_c = (1 - zoneout_prob_c) * F.dropout(forward_new_c, p=hp.dropout_rate,
                                                                 training=self.training) + forward_c
                forward_new_state = forward_new_h, forward_new_c
                forward_output = forward_new_h

            else:
                forward_h = forward_state
                forward_new_h = forward_new_state

                zoneout_prob_h = self.zoneout_prob

                forward_new_h = (1 - zoneout_prob_h) * F.dropout(forward_new_h, p=hp.dropout_rate,
                                                                 training=self.training) + forward_h

                forward_new_state = forward_new_h
                forward_output = forward_new_h
            return forward_output, forward_new_state