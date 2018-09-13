// stoll example
#include <iostream>   // std::cout
#include <string>     // std::string, std::stoll

int main ()
{
  std::string str = "8246821 0xffff 020";

  std::string::size_type sz = 0;   // alias of size_t

  while (!str.empty()) {
    long long ll = std::stoll (str,&sz, 16);
    std::cout << str.substr(0,sz) << " interpreted as " << ll << '\n';
    str = str.substr(sz);
  }

  return 0;
}