#pragma once
#include <map>
#include <string>
namespace flux::symb {
class ExprTree;
}

template <typename Scalar>
Scalar evalExprTree(flux::symb::ExprTree *&&expression_ptr, const std::map<std::string, Scalar> &variables);
