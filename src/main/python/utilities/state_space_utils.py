import numpy as np
import scipy
import scipy.signal


def check_validity(A=None, B=None, C=None, D=None, Q_noise=None, R_noise=None, K=None, L=None):
    """Checks the validity of the system based on the sizes of matrices in the system"""

    if A is not None:
        A = np.asmatrix(A)
    if B is not None:
        B = np.asmatrix(B)
    if C is not None:
        C = np.asmatrix(C)
    if D is not None:
        D = np.asmatrix(D)
    if Q_noise is not None:
        Q_noise = np.asmatrix(Q_noise)
    if R_noise is not None:
        R_noise = np.asmatrix(R_noise)
    if K is not None:
        K = np.asmatrix(K)
    if L is not None:
        L = np.asmatrix(L)

    if A is not None:
        assert A.shape[0] == A.shape[1],                                            \
            "A must be square"

    if A is not None and B is not None:
        assert B.shape[0] == A.shape[0],                                            \
            "A and B must have the same number of rows"

    if A is not None and C is not None:
        assert C.shape[1] == A.shape[0],                                            \
            "C must have as many columns as there are states"

    if D is not None and C is not None:
        assert D.shape[0] == C.shape[0],                                            \
            "C and D must have the same number of rows"
    if D is not None and B is not None:
        assert D.shape[1] == B.shape[1],                                            \
            "B and D must have the same number of columns"

    if Q_noise is not None and A is not None:
        assert Q_noise.shape == A.shape,                                            \
            "Q must have the same dimensions as A"

    if R_noise is not None:
        assert R_noise.shape[0] == R_noise.shape[1],                                \
            "R must be square"
    if R_noise is not None and C is not None:
        assert R_noise.shape[0] == C.shape[0],                                      \
            "R must have the same number of rows as there are sensor inputs"

    if K is not None and B is not None:
        assert K.shape[0] == B.shape[1],                                            \
            "K must have the same number of rows as there are inputs"
    if K is not None and A is not None:
        assert K.shape[1] == A.shape[0],                                            \
            "K must have the same number of columns as there are states"

    if L is not None and A is not None:
        assert L.shape[0] == A.shape[0],                                            \
            "L must have the same number of rows as there are states"
        assert L.shape[1] == C.shape[0],                                            \
            "L must have the same number of columns as there are sensor inputs"


def controllability(A, B):
    """ Creates the controllability matrix from matrices A and C
        If the controllability matrix has full rank, then the system is completely controllable"""

    check_validity(A=A, B=B)

    n = B.shape[1]
    m = A.shape[1]
    ctrb = np.asmatrix(np.zeros((m, m*n)))
    current_submatrix = np.asmatrix(B)

    for i in range(m):
        ctrb[:m, i*n:i*n+n] = current_submatrix
        current_submatrix = A * current_submatrix

    return ctrb


def observability(A, C):
    """ Creates the observability matrix from matrices A and C
        If the observability matrix has full rank, then the system is completely observable"""

    check_validity(A=A, C=C)

    n = C.shape[0]
    m = A.shape[1]
    obsv = np.asmatrix(np.zeros((n*m, m)))
    current_submatrix = np.asmatrix(C)

    for i in range(m):
        obsv[i*n:i*n+n, :m] = current_submatrix
        current_submatrix = current_submatrix * A

    return obsv


def c2d(A, B, Q_noise, R_noise, dt: float):
    """ Convert a continuous-time dynamical system to a discrete time system
        Continuous-time form: dx(t)/t = A*x(t) + B*u(t), where x is a state vector and u is control input
        Discrete-time form: x[k+1] = A*x[k] + B*u[k], where k is an incrementing integer according to preset time steps
    """

    A = np.asmatrix(A)
    B = np.asmatrix(B)
    Q_noise = np.asmatrix(Q_noise)
    R_noise = np.asmatrix(R_noise)
    check_validity(A=A, B=B, Q_noise=Q_noise, R_noise=R_noise)

    n = A.shape[0]
    m = B.shape[1]

    M = np.zeros((n+m, n+m))
    M[:n, :n] = A
    M[:n, n:n+m] = B
    N = np.asmatrix(scipy.linalg.expm(M * dt))

    A_discrete = N[:n, :n]
    B_discrete = N[:n, n:n+m]

    F = np.zeros((n+n, n+n))
    F[:n, :n] = -A
    F[n:, n:] = A.T
    F[:n, n:n+n] = Q_noise
    G = np.asmatrix(scipy.linalg.expm(F * dt))

    Q_noise_discrete = A * G[:n, n:n+n]
    R_noise_discrete = R_noise / dt

    return [A_discrete, B_discrete, Q_noise_discrete, R_noise_discrete]


def clqr(A, B, Q_weight, R_weight):
    """ Return the optimal gain matrix K for controlling the continuous-time system
        according to weight matrices Q_weight and R_weight """

    A = np.asmatrix(A)
    B = np.asmatrix(B)
    Q_weight = np.asmatrix(Q_weight)
    R_weight = np.asmatrix(R_weight)
    check_validity(A=A, B=B)

    # Use scipy's majik powers to solve the Ricatti equation
    P = np.asmatrix(scipy.linalg.solve_continuous_are(A, B, Q_weight, R_weight))

    # Use the matrix that you get from solving the Ricatti equation to solve for the optimal gain matrix K
    # K = R^-1 * B.T * P
    return np.asmatrix(scipy.linalg.inv(R_weight) * B.T * P)


def dlqr(A, B, Q_weight, R_weight):
    """ Return the optimal gain matrix K for controlling the discrete-time system
        according to weight matrices Q_weight and R_weight """

    A = np.asmatrix(A)
    B = np.asmatrix(B)
    Q_weight = np.asmatrix(Q_weight)
    R_weight = np.asmatrix(R_weight)
    check_validity(A=A, B=B)

    # Use scipy's majik powers to solve the Ricatti equation
    P = np.asmatrix(scipy.linalg.solve_discrete_are(A, B, Q_weight, R_weight))

    # Use the matrix that you get from solving the Ricatti equation to solve for the optimal gain matrix K
    # K = (R + B.T * P * B)^-1 * B.T * P * A
    return np.asmatrix(scipy.linalg.inv(R_weight + B.T * P * B) * B.T * P * A)


def discrete_kalman(A, C, Q_noise, R_noise):
    """ Returns the optimal Kalman gain L according to the covariances and system and sensor dynamics
        This function is specifically for discrete-time systems"""

    A = np.asmatrix(A)
    C = np.asmatrix(C)
    Q_noise = np.asmatrix(Q_noise)
    R_noise = np.asmatrix(R_noise)
    check_validity(A=A, C=C)

    # Applying lqr using A.T, C.T, Q, and R actually returns the transpose of the optimal Kalman gain L
    return np.asmatrix(dlqr(A.T, C.T, Q_noise, R_noise)).T

def continuous_kalman(A, C, Q_noise, R_noise):
    """ Returns the optimal Kalman gain L according to the covariances and system and sensor dynamics
        This function is specifically for continuous-time systems"""

    A = np.asmatrix(A)
    C = np.asmatrix(C)
    Q_noise = np.asmatrix(Q_noise)
    R_noise = np.asmatrix(R_noise)
    check_validity(A=A, C=C)

    # Applying lqr using A.T, C.T, Q, and R actually returns the transpose of the optimal Kalman gain L
    return np.asmatrix(clqr(A.T, C.T, Q_noise, R_noise)).T
