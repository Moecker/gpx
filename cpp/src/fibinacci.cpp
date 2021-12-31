#include "fibonacci.h"

unsigned int fibonacci(const unsigned int n)
{
    if (n < 2)
    {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}
