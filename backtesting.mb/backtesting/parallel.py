import multiprocessing as mp
import timeit

def cube(x):
    return x**3

def multi(processors):
    if __name__ == "__main__": 
        pool = mp.Pool(processes=processors)
        results = pool.map(cube, range(1,10))
        print(results)

def serial():
    results = map(cube, range(1,10))
    print(results)

starttime = timeit.default_timer()
multi(4)
print(timeit.default_timer() - starttime)

starttime = timeit.default_timer()
serial()
print(timeit.default_timer() - starttime)

if __name__ == "__main__": 
    pool = mp.Pool()
    results = pool.map(cube, range(1,20))
    pool.close()
    pool.join()
    print(results)
