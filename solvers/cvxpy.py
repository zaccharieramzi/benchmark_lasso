from benchopt.base import BaseSolver
from benchopt.util import safe_import_context


with safe_import_context() as import_ctx:
    import cvxpy as cp


class Solver(BaseSolver):
    name = 'cvxpy'

    install_cmd = 'conda'
    requirements = ['cvxpy']

    def set_objective(self, X, y, lmbd):
        self.X, self.y, self.lmbd = X, y, lmbd

        n_features = self.X.shape[1]
        self.beta = cp.Variable(n_features)

        loss = 0.5 * cp.norm2(self.y - cp.matmul(self.X, self.beta))**2
        self.problem = cp.Problem(cp.Minimize(
            loss + self.lmbd * cp.norm(self.beta, 1)))

        # Hack cvxpy to be able to retrieve a suboptimal solution when
        # reaching max_iter
        cp.reductions.solvers.conic_solvers.ECOS.STATUS_MAP[-1] = \
            'optimal_inaccurate'

        cp.settings.ERROR = ['solver_error']

    def run(self, n_iter):
        self.problem.solve(max_iters=n_iter, verbose=False)

    def get_result(self):
        return self.beta.value.flatten()
