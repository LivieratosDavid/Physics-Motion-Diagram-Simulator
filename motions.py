import numpy as np

g = 9.81

class Motion:
    def __init__(self, v0, t_max):
        self.v0 = v0
        self.t_max = t_max
        self.t = np.linspace(0, t_max, 100)

    def position(self):
        pass

    def kinetic(self):
        pass

class LinearMotion(Motion):
    def position(self):
        return self.v0 * self.t

    def velocity(self):
        return np.full_like(self.t, self.v0)

class AcceleratedMotion(Motion):
    def __init__(self, v0, t_max, a, m):
        super().__init__(v0, t_max)

        self.a = a
        self.mass = m 

    def position(self):
        return self.v0 * self.t + 1/2 * self.a * self.t**2

    def velocity(self):
        return self.v0 + self.a * self.t

    def kinetic(self):
        v = self.velocity()
        return 1/2 * self.mass * v**2

    def dk(self):
        initial_kinetic = 0.5 * self.mass * self.v0**2
        final_kinetic = self.kinetic()[-1]

        return final_kinetic - initial_kinetic

class ProjectileMotion(Motion):
    def __init__(self, v0, t_max, h0, theta, m):
        super().__init__(v0, t_max)

        self.h0 = h0
        self.theta = theta
        self.mass = m

    def angle(self):
        return np.radians(self.theta)

    def vy_initial(self):
        return self.v0 * np.sin(self.angle())

    def vy(self):
        return self.vy_initial() - g * self.t

    def vx(self):
        return self.v0 * np.cos(self.angle())

    def v_full(self):
        return np.sqrt(self.vx() ** 2 + self.vy() ** 2)

    def height(self):
        return self.h0 + self.vy_initial() * self.t - 0.5 * g * self.t**2

    def position(self):
        return self.vx() * self.t

    def kinetic(self):
        return 0.5 * self.mass * self.v_full() ** 2

    def potential(self):
        return self.mass * g * self.height()

    def dk(self):
        initial_kinetic = 0.5 * self.mass * self.v0 ** 2
        final_kinetic = self.kinetic()[-1]

        return final_kinetic - initial_kinetic

    def dU(self):
        initial_potential = self.mass * g * self.h0
        final_potential = self.potential()[-1]

        return final_potential - initial_potential

    def truncate_at_landing(self):
        y = self.height()
        x = self.position()

        landing_index = np.where(y <= 0)[0]

        if len(landing_index) > 0:
            cutoff = landing_index[0] + 1

            self.t = self.t[:cutoff]
            x = x[:cutoff]
            y = y[:cutoff]

        y = np.maximum(y, 0)

        return x, y

class SimpleHarmonicMotion(Motion):
    def __init__(self, v0, t_max, A, k, m):
        super().__init__(v0, t_max)
        self.a = A
        self.k = k
        self.mass = m

    def omega(self):
        return np.sqrt(self.k / self.mass)

    def position(self):
        return self.a * np.cos(self.omega() * self.t)

    def velocity(self):
        return -self.a * self.omega() * np.sin(self.omega() * self.t)

    def kinetic(self):
        return 1/2 * self.mass * self.velocity() ** 2

    def potential(self):
        return 1/2 * self.k * self.position() ** 2