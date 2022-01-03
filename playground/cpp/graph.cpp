#include <iostream>
#include <map>
#include <vector>

void normal_map() {
  std::map<int, int> m{};
  m.insert(std::make_pair(1, 2));

  if (m.find(1) != m.end()) {
    m.find(1)->second = 3;
  }

  for (const auto i : m) {
    std::cout << i.first << std::endl;
    std::cout << i.second << std::endl;
  }
}

void list_map() {
  std::map<int, std::map<int, int>> m{};
  std::map<int, int> i{};
  i.insert(std::make_pair(1, 2));
  m.insert(std::make_pair(3, i));

  if (m.find(3) != m.end()) {
    m.find(3)->second.insert(std::make_pair(4, 5));
  }

  for (const auto i : m) {
    std::cout << i.first << std::endl;
    for (const auto j : i.second) {
      std::cout << j.first << std::endl;
      std::cout << j.second << std::endl;
    }
  }
}

int main() {
  normal_map();
  std::cout << std::endl;
  list_map();
  return 0;
}
