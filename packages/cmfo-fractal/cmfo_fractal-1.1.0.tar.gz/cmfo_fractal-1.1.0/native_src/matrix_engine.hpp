#ifndef MATRIX_ENGINE_HPP
#define MATRIX_ENGINE_HPP

#include <array>
#include <cmath>
#include <complex>
#include <iostream>
#include <vector>

// CMFO Constants
const double PHI = 1.618033988749895;

// Complex number type
using Complex = std::complex<double>;

class Matrix7x7 {
private:
  // Row-major storage: 7x7 = 49 elements
  std::array<Complex, 49> data;

public:
  // Constructors
  Matrix7x7(); // Zero matrix
  static Matrix7x7 Identity();
  static Matrix7x7 Diagonal(const std::array<double, 7> &values);

  // Accessors
  Complex &at(int row, int col);
  const Complex &at(int row, int col) const;

  // Operations
  Matrix7x7 operator*(const Matrix7x7 &other) const; // Composition
  Matrix7x7 operator*(double scalar) const;          // Scaling
  Matrix7x7 operator+(const Matrix7x7 &other) const; // Superposition

  // Analytic Properties
  Matrix7x7 adjoint() const; // Conjugate Transpose
  Complex trace() const;
  bool is_unitary(double epsilon = 1e-9) const;

  // Utils
  void print() const;

  // Raw pointer access for C/Python interop
  Complex *raw_data() { return data.data(); }
};

#endif // MATRIX_ENGINE_HPP
