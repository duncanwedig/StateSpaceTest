import numpy as np
from utilities.state_space.state_space_utils import check_validity, observability, controllability


class Gains(object):
    """ Base class for the two gains variants"""
    pass


class StateSpaceGains(Gains):

    def __init__(self, name, A, B, C, D, Q_noise, R_noise, K, L, Kff, u_min, u_max, dt):
        self.A = np.asmatrix(A)
        self.B = np.asmatrix(B)
        self.C = np.asmatrix(C)
        self.D = np.asmatrix(D)

        self.Q_noise = np.asmatrix(Q_noise)
        self.R_noise = np.asmatrix(R_noise)

        self.K = np.asmatrix(K)
        self.L = np.asmatrix(L)
        self.Kff = np.asmatrix(Kff)

        self.u_min = u_min
        self.u_max = u_max

        self.dt = dt

        self.n = self.A.shape[0]
        self.p = self.B.shape[1]
        self.q = self.C.shape[0]

        self.name = name

        self.is_controllable = self.check_controllability()
        self.is_observable = self.check_observability()

        self.check_system_validity()

    def check_controllability(self):
        return np.linalg.matrix_rank(controllability(self.A, self.B)) == self.A.shape[0]

    def check_observability(self):
        return np.linalg.matrix_rank(observability(self.A, self.C)) == self.A.shape[0]

    def check_system_validity(self):
        check_validity(self.A, self.B, self.C, self.D, self.Q_noise, self.R_noise, self.K, self.L, self.Kff)

    def print_gains(self):
        print('A = ', '\n', self.A)
        print('B = ', '\n', self.B)
        print('C = ', '\n', self.C)
        print('D = ', '\n', self.D)

        print('Q_noise = ', '\n', self.Q_noise)
        print('R_noise = ', '\n', self.R_noise)
        print('K = ', '\n', self.K)
        print('L = ', '\n', self.L)
        print('Kff = ', '\n', self.Kff)

        print('u_min = ', '\n', self.u_min)
        print('u_max = ', '\n', self.u_max)


class ContinuousGains(Gains):
    """ This is a dumb class which I probably ain't using"""

    def __init__(self, A, B, C, D, u_min, u_max, B_ref=None):

        self.A = np.asmatrix(A)
        self.B = np.asmatrix(B)
        self.C = np.asmatrix(C)
        self.D = np.asmatrix(D)

        # Hopefully B_ref * x + A*x = dx/dt = 0
        if B_ref is not None:
            self.B_ref = np.asmatrix(B_ref)
        else:
            self.B_ref = np.linalg.pinv(B) * -self.A

        self.u_min = np.asmatrix(u_min)
        self.u_max = np.asmatrix(u_max)

        self.name = name


class GainsList(object):
    """
    A wrapper around a list of gains. This should really extend list or something, but I'm a bit too lazy to be smart.
    """

    def __init__(self, gains):

        assert isinstance(gains, list) and isinstance(gains[0], Gains)              \
            or isinstance(gains, Gains),                                            \
            "Gains must be an instance of Gains or a list of Gains"

        if isinstance(gains, Gains):
            self.gains_list = [gains]
        else:
            self.gains_list = gains

    # I should really just make this be a subclass of list or something
    def add_gains(self, gains):

        assert isinstance(gains, list) and isinstance(gains[0], Gains)              \
            or isinstance(gains, Gains),                                            \
            "Gains must be an instance of Gains or a list of Gains"

        if isinstance(gains, list):
            self.gains_list += gains
        else:
            self.gains_list.append(gains)

    def get_gains(self, index):
        return self.gains_list[index]

    def __len__(self):
        return len(self.gains_list)
