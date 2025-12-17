#pragma once

#include <boost/preprocessor/seq/for_each_product.hpp>
#include <boost/preprocessor/seq/to_tuple.hpp>

#define MACRO_EXPAND(x) x

/**
 * Macro that converts a call of boost with an argument in sequence form to a direct call to a macro with multiple
 * arguments called `INSTANTIATE`.
 * @param _ Unused, but given by boost PP iterations
 * @param sequence The sequence of values that should be passed to the `INSTANTIATE` macro.
 */
#define calleer(_, sequence) MACRO_EXPAND(INSTANTIATE BOOST_PP_SEQ_TO_TUPLE(sequence))

/**
 * This macro is intended to be used to define explicit instantiations with multiple template parameters.
 * That The typical use case look like this:
 *
 * ```
 *
 * #define INSTANTIATE(class_t, matrix, state) template class your_class<matrix, state>;
 *
 * CROSS_PRODUCT_INSTANTIATE((REAL_MATRIX_TYPES) (STATE_TYPES) )
 *
 * ```
 * @param lists The list of sets that should be "crossed". The individual sets are packed in brackets, like this
 * `(SET_1) (SET_2) ...`. And the individual set follow the same format, so `SET_1` can be something like `(1)(2)(3)`
 */
#define CROSS_PRODUCT_INSTANTIATE(lists) BOOST_PP_SEQ_FOR_EACH_PRODUCT(calleer, lists)

// Defintion of common set of types that are used together with the mechanics defined in this file

/**
 * Set of all (two) boolean values
 * Nothing MFA specific, but booleans combination are used very often
 */
#define BOOL_VALUES (true)(false)
/**
 * All the types that are used as state types by some method
 */
#define STATE_TYPES (RealVector)(RealMatrix)
/**
 * The matrix types that are used during the analyis
 */
#define REAL_MATRIX_TYPES (RealMatrix)(SparseMatrix<Real>)

/**
 * The simple specification for parameters
 */
#define PARA_SPEC (FluxSpecification)(PoolSizeSpecification)
/**
 * The labeling state specifications
 */
#define LABEL_SPEC                                                                                                     \
    (MIMSSpecification)(MSSpecification)(CumomerSpecification)(CNMRSpecification)(HNMRSpecification)(MSMSSpecification)
/**
 * Types of labeling networks
 */
#define NETWORK_TYPES (LabelingNetwork)(ReducedLabelingNetwork)
/**
 * The set of methods that support reducibility
 */
#define REDUCIBLE_METHODS (CumomerMethod)(EMUMethod)
/**
 * The set of method that use cascading
 */
#define CASCADING_METHODS (CumomerMethod)(EMUMethod)
