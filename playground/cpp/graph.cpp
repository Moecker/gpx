#include <iostream>
#include <map>
#include <vector>

int main()
{
    std::cout << "Start" << std::endl;

    std::map<int,int> m{};
    m.insert(std::make_pair(1,2));

    if (m.find(1) != m.end())
    {
        m.find(1)->second = 3;
    }

    for (const auto i : m)
    {
        std::cout << i.first << std::endl;
        std::cout << i.second << std::endl;
    }

    return 0;
}
