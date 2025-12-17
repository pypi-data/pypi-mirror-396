#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <memory>
#include <exception>
#include <string>
#include <vector>

#include "VNNLib.h"                
#include "TypeChecker.h"     
#include "TypedAST.h"     
#include "TypedBuilder.h"
#include "LinearArithExpr.h"
#include "DNFConverter.h"
#include "CompatTransformer.h"
#include "Error.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
	m.doc() = "Python bindings for VNNLib parsing and AST traversal";

	py::register_exception<VNNLibException>(m, "VNNLibException");

	// Helper Types
	py::enum_<TDataType>(m, "DType")
		.value("Real", TDataType::Real)
		.value("F16", TDataType::F16).value("F32", TDataType::F32).value("F64", TDataType::F64).value("BF16", TDataType::BF16)
		.value("F8E4M3FN", TDataType::F8E4M3FN).value("F8E5M2", TDataType::F8E5M2)
		.value("F8E4M3FNUZ", TDataType::F8E4M3FNUZ).value("F8E5M2FNUZ", TDataType::F8E5M2FNUZ)
		.value("F4E2M1", TDataType::F4E2M1)
		.value("I8", TDataType::I8).value("I16", TDataType::I16).value("I32", TDataType::I32).value("I64", TDataType::I64)
		.value("U8", TDataType::U8).value("U16", TDataType::U16).value("U32", TDataType::U32).value("U64", TDataType::U64)
		.value("C64", TDataType::C64).value("C128", TDataType::C128)
		.value("Bool", TDataType::Bool).value("String", TDataType::String)
		.value("Unknown", TDataType::Unknown)
		.value("NegativeIntConstant", TDataType::NegativeIntConstant)
		.value("PositiveIntConstant", TDataType::PositiveIntConstant)
		.value("FloatConstant", TDataType::FloatConstant);

	py::enum_<SymbolKind>(m, "SymbolKind")
		.value("Input", SymbolKind::Input)
		.value("Hidden", SymbolKind::Hidden)
		.value("Output", SymbolKind::Output)
		.value("Unknown", SymbolKind::Unknown);

	py::class_<TNode>(m, "Node")
		.def("__str__", [](const TNode& n){ return n.toString(); })
		.def("children", [](py::object self){ 
			const TNode& n = self.cast<const TNode&>();
			std::vector<const TNode*> children;
			n.children(children);
			py::tuple out(children.size());

			for (int i = 0; i < children.size(); ++i) {
				out[i] = py::cast(children[i], py::return_value_policy::reference_internal, self);
			}
			return out;
		});

	// --- LinearArithExpr ---
	py::class_<LinearArithExpr::Term>(m, "Term")
		.def_property_readonly("coeff",    [](const LinearArithExpr::Term& t){ return t.coeff; })
		.def_property_readonly("var", [](const LinearArithExpr::Term& t){ return t.var; }, py::return_value_policy::reference_internal)
		.def_property_readonly("var_name", [](const LinearArithExpr::Term& t){ return t.varName; });

	py::class_<LinearArithExpr>(m, "LinearArithExpr")
		.def_property_readonly("terms", [](const LinearArithExpr& e){ return e.getTerms(); })
		.def_property_readonly("constant", [](const LinearArithExpr& e){ return e.getConstant(); });

	// --- Arithmetic Operations --- 
	py::class_<TArithExpr, TNode>(m, "ArithExpr")
		.def_property_readonly("dtype", [](const TArithExpr& e){ return e.dtype; })
		.def("to_linear_expr", [](const TArithExpr& e){
			auto lin_expr = linearize(&e);
			return py::cast(lin_expr.release(), py::return_value_policy::take_ownership);
		});

	py::class_<TVarExpr, TArithExpr>(m, "Var")
		.def_property_readonly("name",      [](const TVarExpr& v){ return v.symbol ? v.symbol->name : std::string{}; })
		.def_property_readonly("onnx_name", [](const TVarExpr& v)->py::object{
			if (v.symbol->onnxName.empty()) return py::none();
			return py::str(v.symbol->onnxName);
		})
		.def_property_readonly("dtype",       [](const TVarExpr& v){ return v.symbol->dtype; })
		.def_property_readonly("shape",       [](const TVarExpr& v){ return v.symbol->shape; })
		.def_property_readonly("kind",        [](const TVarExpr& v){ return v.symbol->kind; })
		.def_property_readonly("network_name",[](const TVarExpr& v){ return v.symbol->networkName; })
		.def_property_readonly("indices",     [](const TVarExpr& v){ return v.indices; })
		.def_property_readonly("line",        [](const TVarExpr& v){ return v.line; });

	py::class_<TLiteral, TArithExpr>(m, "Literal")
		.def_property_readonly("lexeme", [](const TLiteral& e){ return e.lexeme; })
		.def_property_readonly("line",   [](const TLiteral& e){ return e.line; });

	py::class_<TFloat, TLiteral>(m, "Float")
		.def_property_readonly("value", [](const TFloat& n){ return n.value; });

	py::class_<TInt, TLiteral>(m, "Int")
		.def_property_readonly("value", [](const TInt& n){ return n.value; });

	py::class_<TNegate, TArithExpr>(m, "Negate")
		.def_property_readonly("expr", [](const TNegate& n){ return n.expr.get(); }, py::return_value_policy::reference_internal);

	py::class_<TPlus, TArithExpr>(m, "Plus")
	.def_property_readonly("args", [](const TPlus& n){
		py::tuple args_tuple(n.args.size());
		for (size_t i = 0; i < n.args.size(); ++i)
			args_tuple[i] = py::cast(n.args[i].get(), py::return_value_policy::reference_internal, py::cast(&n));
		return args_tuple;
	});

	py::class_<TMinus, TArithExpr>(m, "Minus")
	.def_property_readonly("head", [](const TMinus& n){ return n.head.get(); }, py::return_value_policy::reference_internal)
	.def_property_readonly("rest", [](const TMinus& n){
		py::tuple rest_tuple(n.rest.size());
		for (size_t i = 0; i < n.rest.size(); ++i)
			rest_tuple[i] = py::cast(n.rest[i].get(), py::return_value_policy::reference_internal, py::cast(&n));
		return rest_tuple;
	});

	py::class_<TMultiply, TArithExpr>(m, "Multiply")
	.def_property_readonly("args", [](const TMultiply& n){
		py::tuple args_tuple(n.args.size());
		for (size_t i = 0; i < n.args.size(); ++i)
			args_tuple[i] = py::cast(n.args[i].get(), py::return_value_policy::reference_internal, py::cast(&n));
		return args_tuple;
	});

  	// ---------- Boolean Operations ----------
	py::class_<TBoolExpr, TNode>(m, "BoolExpr")
		.def("to_dnf", [](const TBoolExpr& e){
			DNF dnf = toDNF(&e);
			py::list py_dnf;

			for (size_t i = 0; i < dnf.size(); ++i) {
				auto& clause = dnf[i];
				py::list py_clause;
				for (auto* lit : clause) {
					py_clause.append(py::cast(lit, py::return_value_policy::reference_internal, py::cast(&e)));
				}
				py_dnf.append(py_clause);
			}
			return py_dnf;
		});

	py::class_<TCompare, TBoolExpr>(m, "Comparison")
		.def_property_readonly("lhs", [](const TCompare& n){ return n.lhs.get(); }, py::return_value_policy::reference_internal)
		.def_property_readonly("rhs", [](const TCompare& n){ return n.rhs.get(); }, py::return_value_policy::reference_internal);

	py::class_<TGreaterThan, TCompare>(m, "GreaterThan");
	py::class_<TEqual, TCompare>(m, "Equal");
	py::class_<TLessThan, TCompare>(m, "LessThan");
	py::class_<TGreaterEqual, TCompare>(m, "GreaterEqual");
	py::class_<TLessEqual, TCompare>(m, "LessEqual");
	py::class_<TNotEqual, TCompare>(m, "NotEqual");

	py::class_<TConnective, TBoolExpr>(m, "Connective")
		.def_property_readonly("args", [](const TConnective& n){
			py::tuple args_tuple(n.args.size());
			for (size_t i = 0; i < n.args.size(); ++i)
				args_tuple[i] = py::cast(n.args[i].get(), py::return_value_policy::reference_internal, py::cast(&n));
			return args_tuple;
		});

	py::class_<TAnd, TConnective>(m, "And");
	py::class_<TOr, TConnective>(m, "Or");

	// --- Assertion ---
	py::class_<TAssertion, TNode>(m, "Assertion")
		.def_property_readonly("expr", [](const TAssertion& a){ return a.cond.get(); }, py::return_value_policy::reference_internal);
	
	// --- Definitions ---
	py::class_<TInputDefinition, TNode>(m, "InputDefinition")
		.def_property_readonly("name", [](const TInputDefinition& d){ return d.symbol ? d.symbol->name : std::string{}; })
		.def_property_readonly("onnx_name", [](const TInputDefinition& d)->py::object{
			if (d.symbol->onnxName.empty()) return py::none();
			return py::str(d.symbol->onnxName);
		})
		.def_property_readonly("dtype", [](const TInputDefinition& d){ return d.symbol ? d.symbol->dtype : TDataType::Unknown; })
		.def_property_readonly("shape", [](const TInputDefinition& d){ return d.symbol ? d.symbol->shape : Shape{}; })
		.def_property_readonly("kind",  [](const TInputDefinition& d){ return d.symbol ? d.symbol->kind : SymbolKind::Unknown; })
		.def_property_readonly("network_name", [](const TInputDefinition& d){ return d.symbol ? d.symbol->networkName : std::string{}; });

	py::class_<THiddenDefinition, TNode>(m, "HiddenDefinition")
		.def_property_readonly("name", [](const THiddenDefinition& d){ return d.symbol ? d.symbol->name : std::string{}; })
		.def_property_readonly("onnx_name", [](const THiddenDefinition& d)->py::object{
			if (d.symbol->onnxName.empty()) return py::none();
			return py::str(d.symbol->onnxName);
		})
		.def_property_readonly("dtype", [](const THiddenDefinition& d){ return d.symbol ? d.symbol->dtype : TDataType::Unknown; })
		.def_property_readonly("shape", [](const THiddenDefinition& d){ return d.symbol ? d.symbol->shape : Shape{}; })
		.def_property_readonly("kind",  [](const THiddenDefinition& d){ return d.symbol ? d.symbol->kind : SymbolKind::Unknown; })
		.def_property_readonly("network_name", [](const THiddenDefinition& d){ return d.symbol ? d.symbol->networkName : std::string{}; });

	py::class_<TOutputDefinition, TNode>(m, "OutputDefinition")
		.def_property_readonly("name", [](const TOutputDefinition& d){ return d.symbol ? d.symbol->name : std::string{}; })
		.def_property_readonly("onnx_name", [](const TOutputDefinition& d)->py::object{
			if (d.symbol->onnxName.empty()) return py::none();
			return py::str(d.symbol->onnxName);
		})
		.def_property_readonly("dtype", [](const TOutputDefinition& d){ return d.symbol ? d.symbol->dtype : TDataType::Unknown; })
		.def_property_readonly("shape", [](const TOutputDefinition& d){ return d.symbol ? d.symbol->shape : Shape{}; })
		.def_property_readonly("kind",  [](const TOutputDefinition& d){ return d.symbol ? d.symbol->kind : SymbolKind::Unknown; })
		.def_property_readonly("network_name", [](const TOutputDefinition& d){ return d.symbol ? d.symbol->networkName : std::string{}; });

	// --- Network ---
	py::class_<TNetworkDefinition, TNode>(m, "Network")
	.def_property_readonly("name", [](const TNetworkDefinition& n){ return n.networkName; })
	.def_property_readonly("isometric_to", [](const TNetworkDefinition& n){ return n.isometricTo; })
	.def_property_readonly("equal_to", [](const TNetworkDefinition& n){ return n.equalTo; })
	.def_property_readonly("inputs", [](const TNetworkDefinition& n){
		py::tuple input_tuple(n.inputs.size());
		for (size_t i = 0; i < n.inputs.size(); ++i)
			input_tuple[i] = py::cast(n.inputs[i].get(), py::return_value_policy::reference_internal, py::cast(&n));
		return input_tuple;
	})
	.def_property_readonly("hidden", [](const TNetworkDefinition& n){
		py::tuple hidden_tuple(n.hidden.size());
		for (size_t i = 0; i < n.hidden.size(); ++i)
			hidden_tuple[i] = py::cast(n.hidden[i].get(), py::return_value_policy::reference_internal, py::cast(&n));
		return hidden_tuple;
	})
	.def_property_readonly("outputs", [](const TNetworkDefinition& n){
		py::tuple output_tuple(n.outputs.size());
		for (size_t i = 0; i < n.outputs.size(); ++i)
			output_tuple[i] = py::cast(n.outputs[i].get(), py::return_value_policy::reference_internal, py::cast(&n));
		return output_tuple;
	});

	// --- Version ---
	py::class_<TVersion, TNode>(m, "Version")
		.def_property_readonly("major", [](const TVersion& v){ return v.major; })
		.def_property_readonly("minor", [](const TVersion& v){ return v.minor; });

	// --- Query ---
	py::class_<TQuery, TNode>(m, "Query")
    .def_property_readonly("networks", [](const TQuery& q){
		py::tuple network_tuple(q.networks.size());
		for (size_t i = 0; i < q.networks.size(); ++i)
			network_tuple[i] = py::cast(q.networks[i].get(), py::return_value_policy::reference_internal, py::cast(&q));
		return network_tuple;
	})
    .def_property_readonly("assertions", [](const TQuery& q){
		py::tuple assertion_tuple(q.assertions.size());
		for (size_t i = 0; i < q.assertions.size(); ++i)
			assertion_tuple[i] = py::cast(q.assertions[i].get(), py::return_value_policy::reference_internal, py::cast(&q));
		return assertion_tuple;
	});

	// --- CompatTransformer ---
	py::class_<Polytope>(m, "Polytope")
		.def_property_readonly("coeff_matrix", [](const Polytope& p){ return p.coeffMatrix; })
		.def_property_readonly("rhs", [](const Polytope& p){ return p.rhs; });
	
	py::class_<SpecCase>(m, "SpecCase")
		.def_property_readonly("input_box", [](const SpecCase& c){ return c.inputBox; })
		.def_property_readonly("output_constraints", [](const SpecCase& c){ return c.outputConstraints; },
								py::return_value_policy::reference_internal);

	// --- API ---
	m.def("parse_query_file", [](const std::string& path) {
		return parseQueryFile(path);
	},
	py::return_value_policy::move,
	py::arg("path"));
	
	m.def("parse_query_string", [](const std::string& content) {
		return parseQueryString(content);
	},
	py::return_value_policy::move,
	py::arg("content"));

	m.def("transform_to_compat", [](const TQuery& query) {
		CompatTransformer transformer(&query);
		const auto& cases = transformer.transform();

		py::list py_cases;
		for (const auto& c : cases) {
			py_cases.append(py::cast(c, py::return_value_policy::move));
		}
		return py_cases;
	},
	py::arg("query"));

	m.attr("__version__") = "0.2.0";
}

