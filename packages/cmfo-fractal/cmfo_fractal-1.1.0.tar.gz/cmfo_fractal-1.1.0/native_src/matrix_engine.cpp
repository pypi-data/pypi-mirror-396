#include "matrix_engine.hpp"
#include <Python.h>
#include <iomanip>

#ifdef _OPENMP
#include <omp.h>
#endif

Matrix7x7::Matrix7x7() { data.fill(Complex(0, 0)); }

Matrix7x7 Matrix7x7::Identity() {
  Matrix7x7 m;
  for (int i = 0; i < 7; ++i) {
    m.at(i, i) = Complex(1.0, 0.0);
  }
  return m;
}

Matrix7x7 Matrix7x7::Diagonal(const std::array<double, 7> &values) {
  Matrix7x7 m;
  for (int i = 0; i < 7; ++i) {
    m.at(i, i) = Complex(values[i], 0.0);
  }
  return m;
}

Complex &Matrix7x7::at(int row, int col) { return data[row * 7 + col]; }

const Complex &Matrix7x7::at(int row, int col) const {
  return data[row * 7 + col];
}

Matrix7x7 Matrix7x7::operator*(const Matrix7x7 &other) const {
  Matrix7x7 result;
  // Standard Matrix Multiplication
  for (int i = 0; i < 7; ++i) {
    for (int j = 0; j < 7; ++j) {
      Complex sum(0, 0);
      for (int k = 0; k < 7; ++k) {
        sum += this->at(i, k) * other.at(k, j);
      }
      result.at(i, j) = sum;
    }
  }
  return result;
}

Matrix7x7 Matrix7x7::operator*(double scalar) const {
  Matrix7x7 result;
  for (int i = 0; i < 49; ++i) {
    result.data[i] = this->data[i] * scalar;
  }
  return result;
}

Matrix7x7 Matrix7x7::operator+(const Matrix7x7 &other) const {
  Matrix7x7 result;
  for (int i = 0; i < 49; ++i) {
    result.data[i] = this->data[i] + other.data[i];
  }
  return result;
}

Matrix7x7 Matrix7x7::adjoint() const {
  Matrix7x7 adj;
  for (int i = 0; i < 7; ++i) {
    for (int j = 0; j < 7; ++j) {
      adj.at(j, i) = std::conj(this->at(i, j));
    }
  }
  return adj;
}

Complex Matrix7x7::trace() const {
  Complex tr(0, 0);
  for (int i = 0; i < 7; ++i) {
    tr += this->at(i, i);
  }
  return tr;
}

bool Matrix7x7::is_unitary(double epsilon) const {
  Matrix7x7 prod = (*this) * this->adjoint();
  Matrix7x7 id = Matrix7x7::Identity();

  // Check norm difference
  double error = 0.0;
  for (int i = 0; i < 49; ++i) {
    error += std::abs(prod.data[i] - id.data[i]);
  }

  return error < epsilon;
}

void Matrix7x7::print() const {
  std::cout << std::fixed << std::setprecision(3);
  for (int i = 0; i < 7; ++i) {
    std::cout << "[ ";
    for (int j = 0; j < 7; ++j) {
      const Complex &c = at(i, j);
      std::cout << c.real();
      if (c.imag() >= 0)
        std::cout << "+" << c.imag() << "j ";
      else
        std::cout << c.imag() << "j ";
    }
    std::cout << "]" << std::endl;
  }
}

extern "C" {
#ifdef _WIN32
#define CMFO_API __declspec(dllexport)
#else
#define CMFO_API
#endif

CMFO_API void *Matrix7x7_Create() { return new Matrix7x7(); }
CMFO_API void Matrix7x7_Destroy(void *ptr) {
  delete static_cast<Matrix7x7 *>(ptr);
}

CMFO_API void Matrix7x7_SetIdentity(void *ptr) {
  if (ptr)
    *static_cast<Matrix7x7 *>(ptr) = Matrix7x7::Identity();
}

CMFO_API void Matrix7x7_Multiply(void *a, void *b, void *out) {
  if (a && b && out) {
    *static_cast<Matrix7x7 *>(out) =
        (*static_cast<Matrix7x7 *>(a)) * (*static_cast<Matrix7x7 *>(b));
  }
}

CMFO_API void Matrix7x7_Apply(void *mat_ptr, double *input_vec_real,
                              double *input_vec_imag, double *out_vec_real,
                              double *out_vec_imag) {
  if (!mat_ptr)
    return;
  auto *mat = static_cast<Matrix7x7 *>(mat_ptr);

  // Manual unrolled 7x7 multiplication for simple pointer arrays
  for (int i = 0; i < 7; i++) {
    std::complex<double> sum(0, 0);
    for (int j = 0; j < 7; j++) {
      std::complex<double> vec_val(input_vec_real[j], input_vec_imag[j]);
      sum += mat->at(i, j) * vec_val;
    }
    out_vec_real[i] = sum.real();
    out_vec_imag[i] = sum.imag();
  }
}

CMFO_API void Matrix7x7_Get(void *ptr, double *buffer_real,
                            double *buffer_imag) {
  if (!ptr)
    return;
  auto *mat = static_cast<Matrix7x7 *>(ptr);
  auto *data = mat->raw_data();
  for (int i = 0; i < 49; i++) {
    auto c = data[i];
    buffer_real[i] = c.real();
    buffer_imag[i] = c.imag();
  }
}

CMFO_API void Matrix7x7_Evolve(void *mat_ptr, double *vec_real,
                               double *vec_imag, int steps) {
  if (!mat_ptr)
    return;
  auto *mat = static_cast<Matrix7x7 *>(mat_ptr);

  // Optimize: Use raw pointers and minimize object creation overhead
  auto *mat_data = mat->raw_data();

  // Pre-calculate gamma constants if any (none for pure sin)

  // Use stack arrays for state to keep it hot in L1 cache
  double state_r[7];
  double state_i[7];
  double next_r[7];
  double next_i[7];

  // Load state
  for (int i = 0; i < 7; ++i) {
    state_r[i] = vec_real[i];
    state_i[i] = vec_imag[i];
  }

  // CORE EVOLUTION LOOP - HOT PATH
  for (int s = 0; s < steps; ++s) {
    // 1. Matrix Multiplication (7x7 unrolled inner loops)
    for (int r = 0; r < 7; ++r) {
      double acc_r = 0.0;
      double acc_i = 0.0;
      const int row_offset = r * 7;

      // Unrolling helps modern CPUs pipelining
      for (int c = 0; c < 7; ++c) {
        // Complex mul: (ar + ai*j) * (br + bi*j) = (ar*br - ai*bi) + (ar*bi +
        // ai*br)j mat[r,c] * state[c]
        int idx = row_offset + c;
        double mr = mat_data[idx].real();
        double mi = mat_data[idx].imag();
        double vr = state_r[c];
        double vi = state_i[c];

        acc_r += (mr * vr - mi * vi);
        acc_i += (mr * vi + mi * vr);
      }
      next_r[r] = acc_r;
      next_i[r] = acc_i;
    }

    // 2. Gamma Activation: v = sin(v)
    // Complex sin(a + bj) = sin(a)cosh(b) + i cos(a)sinh(b)
    for (int i = 0; i < 7; ++i) {
      double nr = next_r[i];
      double ni = next_i[i];

      // Fast approximation or standard lib? Standard lib for precision physics.
      // But we separate components manually to avoid std::complex overhead if
      // possible. Standard std::sin(std::complex) is usually well optimized,
      // but let's stick to doubles for transparency or just use std::sin on the
      // complex object if we reconstruct it. Manual implementation for maximum
      // C optimization:
      state_r[i] = std::sin(nr) * std::cosh(ni);
      state_i[i] = std::cos(nr) * std::sinh(ni);
    }
  }

  // Save back
  for (int i = 0; i < 7; ++i) {
    vec_real[i] = state_r[i];
    vec_imag[i] = state_i[i];
  }
}

CMFO_API void Matrix7x7_BatchEvolve(void *mat_ptr, double *batch_real,
                                    double *batch_imag, int batch_size,
                                    int steps) {
  if (!mat_ptr)
    return;
  auto *mat = static_cast<Matrix7x7 *>(mat_ptr);
  auto *mat_data = mat->raw_data();

  // OpenMP include moved to top of file

  // ... (existing code)

  // PARALLEL FRACTAL SUPERPOSITION
  // Process N independent states effectively in parallel
  // This simulates "Superposition of Fractal Timelines"

#ifdef _OPENMP
#pragma omp parallel for
#endif
  for (int idx = 0; idx < batch_size; idx++) {
    // Each node (state) has 7 components.
    // batch arrays are flat: [r0_n0, ... r6_n0, r0_n1, ... ]
    int offset = idx * 7;

    // Load State from Batch
    // Use raw doubles to avoid complex<overhead> in thread-local storage,
    // although std::complex on stack is usually fine.

    double state_r[7];
    double state_i[7];
    double next_r[7];
    double next_i[7];

    for (int i = 0; i < 7; ++i) {
      state_r[i] = batch_real[offset + i];
      state_i[i] = batch_imag[offset + i];
    }

    // Evolve Timeline
    for (int s = 0; s < steps; ++s) {
      // 1. Matrix Multiplication (7x7 unrolled)
      for (int r = 0; r < 7; ++r) {
        double acc_r = 0.0;
        double acc_i = 0.0;
        const int row_offset = r * 7;

        for (int c = 0; c < 7; ++c) {
          int mat_idx = row_offset + c;
          double mr = mat_data[mat_idx].real();
          double mi = mat_data[mat_idx].imag();
          double vr = state_r[c];
          double vi = state_i[c];

          acc_r += (mr * vr - mi * vi);
          acc_i += (mr * vi + mi * vr);
        }
        next_r[r] = acc_r;
        next_i[r] = acc_i;
      }

      // 2. Gamma Activation
      for (int i = 0; i < 7; ++i) {
        double nr = next_r[i];
        double ni = next_i[i];
        state_r[i] = std::sin(nr) * std::cosh(ni);
        state_i[i] = std::cos(nr) * std::sinh(ni);
      }
    }

    // Save Back
    for (int i = 0; i < 7; ++i) {
      batch_real[offset + i] = state_r[i];
      batch_imag[offset + i] = state_i[i];
    }
  }
}

CMFO_API void Matrix7x7_Set(void *ptr, double *buffer_real,
                            double *buffer_imag) {
  if (!ptr)
    return;
  auto *mat = static_cast<Matrix7x7 *>(ptr);
  auto *data = mat->raw_data();
  for (int i = 0; i < 49; i++) {
    data[i] = std::complex<double>(buffer_real[i], buffer_imag[i]);
  }
}
}

// Python Module Boilerplate
static PyModuleDef CmfoCoreNativeModule = {PyModuleDef_HEAD_INIT,
                                           "cmfo_core_native",
                                           "CMFO Core Native Engine",
                                           -1,
                                           NULL,
                                           NULL,
                                           NULL,
                                           NULL,
                                           NULL};

PyMODINIT_FUNC PyInit_cmfo_core_native(void) {
  return PyModule_Create(&CmfoCoreNativeModule);
}
