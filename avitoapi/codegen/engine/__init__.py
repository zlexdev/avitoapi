# Portable OpenAPI → SDK codegen engine.
#
# Everything here is host-agnostic: given a parsed spec IR (:mod:`avitoapi.codegen.parser`)
# and the small Avito config tables (:mod:`avitoapi.codegen.config`), it builds and emits the
# generated surface. Lift the whole ``codegen/`` package elsewhere and swap ``config`` +
# ``fetch`` + ``parser`` to retarget another OpenAPI-described API.
