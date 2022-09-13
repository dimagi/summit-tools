from itertools import islice, repeat, chain


def take(iterable, n):
    return list(islice(iterable, n))


def fill(iterable, n, filler=None):
    return take(pad(iterable, filler), n)


def pad(iterable, filler=None):
    return chain(iterable, repeat(filler))


def transpose(matrix):
    n_cols = len(matrix)
    max_len = max(len(col) for col in matrix)
    return [
        [matrix[i][j] for i in range(n_cols)]
        for j in range(max_len)
    ]
