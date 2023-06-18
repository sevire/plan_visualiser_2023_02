/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./ui_src/drawing.ts":
/*!***************************!*\
  !*** ./ui_src/drawing.ts ***!
  \***************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   initialise_canvas: () => (/* binding */ initialise_canvas)\n/* harmony export */ });\nfunction initialise_canvas(settings) {\n    let canvas = document.getElementById(\"visual\");\n    console.log(\"Canvas = \" + canvas);\n    const res = canvas.getContext('2d');\n    if (!res || !(res instanceof CanvasRenderingContext2D)) {\n        throw new Error('Failed to get 2D context');\n    }\n    const context = res;\n    console.log(\"context = \" + context);\n    let baseCanvasWidth = settings.canvas_width;\n    let baseCanvasHeight = settings.canvas_height;\n    canvas.style.width = baseCanvasWidth + \"px\";\n    canvas.style.height = baseCanvasHeight + \"px\";\n    canvas.width = Math.floor(baseCanvasWidth * window.devicePixelRatio);\n    canvas.height = Math.floor(baseCanvasHeight * window.devicePixelRatio);\n    context.scale(window.devicePixelRatio, window.devicePixelRatio);\n    console.log(\"devicePixelRation: \" + window.devicePixelRatio);\n    console.log(\"After scaling... canvas.width:\" + canvas.width + \" canvas.height\" + canvas.height);\n    context.fillStyle = \"pink\";\n    context.strokeStyle = \"green\";\n    context.lineWidth = 3;\n    context.rect(0, 0, canvas.width, canvas.height);\n    context.fill();\n    context.stroke();\n    // context.fillRect(0, 0, canvas.width, canvas.height)\n    // context.strokeRect(0, 0, canvas.width, canvas.height)\n    return context;\n}\n\n\n//# sourceURL=webpack://plan-visualiser/./ui_src/drawing.ts?");

/***/ }),

/***/ "./ui_src/index.ts":
/*!*************************!*\
  !*** ./ui_src/index.ts ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _drawing__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./drawing */ \"./ui_src/drawing.ts\");\n/* harmony import */ var _plot_shapes__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./plot_shapes */ \"./ui_src/plot_shapes.ts\");\n/* harmony import */ var _visual__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./visual */ \"./ui_src/visual.ts\");\n\n\n\nwindow.addEventListener('DOMContentLoaded', () => {\n    const visual = (0,_visual__WEBPACK_IMPORTED_MODULE_2__[\"default\"])();\n    const visual_settings = visual['settings'];\n    const visual_activities = visual['shapes'];\n    let context = (0,_drawing__WEBPACK_IMPORTED_MODULE_0__.initialise_canvas)(visual_settings);\n    (0,_plot_shapes__WEBPACK_IMPORTED_MODULE_1__.plot_visual)(context, visual_activities, visual_settings);\n});\n\n\n//# sourceURL=webpack://plan-visualiser/./ui_src/index.ts?");

/***/ }),

/***/ "./ui_src/plot_shapes.ts":
/*!*******************************!*\
  !*** ./ui_src/plot_shapes.ts ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   plot_visual: () => (/* binding */ plot_visual)\n/* harmony export */ });\nconst scale_factor = 1.0; // to ensure that visual works on screen (may tweak value)\nfunction plot_rectangle(plot_data) {\n    console.log(\"Plotting rectangle...\");\n    console.log(\"left:\" + plot_data.shape_data.left + \", top:\" + plot_data.shape_data.top);\n    console.log(\"width:\" + plot_data.shape_data.width + \", height:\" + plot_data.shape_data.height);\n    plot_data.ctx.fillStyle = \"blue\";\n    plot_data.ctx.strokeStyle = \"white\";\n    plot_data.ctx.lineWidth = 1;\n    plot_data.ctx.fillRect(plot_data.shape_data.left, plot_data.shape_data.top, plot_data.shape_data.width, plot_data.shape_data.height);\n    plot_data.ctx.strokeRect(plot_data.shape_data.left, plot_data.shape_data.top, plot_data.shape_data.width, plot_data.shape_data.height);\n}\nfunction plot_diamond(plot_data) {\n    const width_height_ratio = 0.7;\n    const context = plot_data.ctx;\n    const shape_data = plot_data.shape_data;\n    context.beginPath();\n    context.moveTo(shape_data.left, shape_data.top);\n    // top left edge\n    context.lineTo(shape_data.left - (shape_data.width * width_height_ratio) / 2, shape_data.top + shape_data.height / 2);\n    // bottom left edge\n    context.lineTo(shape_data.left, shape_data.top + shape_data.height);\n    // bottom right edge\n    context.lineTo(shape_data.left + (shape_data.width * width_height_ratio) / 2, shape_data.top + shape_data.height / 2);\n    // closing the path automatically creates\n    // the top right edge\n    context.closePath();\n    context.fillStyle = \"red\";\n    context.fill();\n}\nfunction plot_text(context, text) {\n}\nconst dispatch_table = {\n    \"RECTANGLE\": plot_rectangle,\n    \"DIAMOND\": plot_diamond,\n};\nfunction plot_visual(ctx, shapes, settings) {\n    for (let shape of shapes) {\n        const shape_details = shape.shape_details;\n        const shape_name = shape_details.shape_name;\n        let shape_plot_dims = shape.shape_details.shape_plot_dims;\n        // Scale all dimensions by scale_factor\n        let k;\n        for (k in shape_plot_dims) {\n            shape_plot_dims[k] *= scale_factor;\n        }\n        const plot_function = dispatch_table[shape_name];\n        const params = { ctx: ctx, shape_data: shape_plot_dims };\n        plot_function(params);\n        // Now plot text\n        plot_text(ctx, \"\");\n    }\n}\n\n\n//# sourceURL=webpack://plan-visualiser/./ui_src/plot_shapes.ts?");

/***/ }),

/***/ "./ui_src/visual.ts":
/*!**************************!*\
  !*** ./ui_src/visual.ts ***!
  \**************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (/* binding */ get_activity_data)\n/* harmony export */ });\nfunction get_activity_data() {\n    let json_activities = document.getElementById(\"json_activities\");\n    console.log(\"json_activities - \" + json_activities);\n    if (json_activities.textContent == null) {\n        return {};\n    }\n    else {\n        return JSON.parse(json_activities.textContent);\n    }\n}\n\n\n//# sourceURL=webpack://plan-visualiser/./ui_src/visual.ts?");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	var __webpack_exports__ = __webpack_require__("./ui_src/index.ts");
/******/ 	
/******/ })()
;