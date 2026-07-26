import numpy as np

class PCA_Python():
    def __init__(self , X : list[list] , n : int):
        self.X = X
        self.n = n
        self._standardize()
        self.__transpose()
        self.__covariance_matrix()

    #https://www.geeksforgeeks.org/python/transpose-matrix-single-line-python/
    #https://medium.com/@cristianleo120/principal-component-analysis-pca-from-scratch-in-python-65998c681bc0

    def _standardize(self):
        n_rows = len(self.X)
        n_cols = len(self.X[0])

        self.means = []
        self.stds = []

        for col in range(n_cols):
            col_values = [self.X[row][col] for row in range(n_rows)]
            mean = sum(col_values) / n_rows
            variance = sum((v - mean) ** 2 for v in col_values) / (n_rows - 1)
            std = variance ** 0.5
            if std == 0:
                std = 1e-8  # or drop the column entirely, since it carries no info
            self.means.append(mean)
            self.stds.append(std)

        self.X = [
            [(self.X[row][col] - self.means[col]) / self.stds[col] for col in range(n_cols)]
            for row in range(n_rows)
        ]


    def __transpose(self):
        self.X_transposed = [list(row) for row in zip(*self.X)]

    def __dot_product(self , A , B):
        result = [[0 for _ in range(len(B[0]))] for _ in range(len(A))]

        for i in range(len(A)):        
            for j in range(len(B[0])): 
                for k in range(len(B)):  
                    result[i][j] += A[i][k] * B[k][j]

        return result

    

    def __covariance_matrix(self):
        n = len(self.X)
        dot_product = self.__dot_product(self.X_transposed , self.X)
        self.cov_matrix = [[val / (n - 1) for val in row] for row in dot_product]

    def __fit(self, n=2):
        cov = np.array(self.cov_matrix)
        if not np.isfinite(cov).all():
            raise ValueError("cov_matrix contains NaN/inf — check for zero-variance columns or missing data in input")
        eigenvalues, eigenvectors = np.linalg.eigh(cov)

        self.eigenvalues = eigenvalues[::-1]
        self.eigenvectors = eigenvectors[:, ::-1]
        self.projection_matrix = self.eigenvectors[:, :n].tolist()

    def get_PCA(self) :
        self.__fit(self.n)
        projected = self.__dot_product(self.X , self.projection_matrix)
        
        explained_variance = (self.eigenvalues[:self.n].sum() / self.eigenvalues.sum())

        return projected , explained_variance
