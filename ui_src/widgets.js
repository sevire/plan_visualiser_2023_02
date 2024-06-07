var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { get_visual_activity_data } from "./plan_visualiser_api";
import { plot_visual } from "./plot_visual";
export class Dropdown {
    constructor(id, activity_unique_id, options, select_handler) {
        this.activity_unique_id = activity_unique_id;
        this.options = options;
        this.element = document.getElementById(id);
        this.selectedOption = this.options[0][0];
        this.select_handler = select_handler;
        this.generate();
    }
    generate() {
        return __awaiter(this, void 0, void 0, function* () {
            const select = document.createElement('select');
            select.id = "select_element";
            this.options.forEach(option => {
                const option_text = option[0];
                const option_id = option[1];
                const optElement = document.createElement('option');
                optElement.text = option_text;
                optElement.value = option_text;
                optElement.id = option_id.toString();
                select.add(optElement);
            });
            select.addEventListener('change', (event) => __awaiter(this, void 0, void 0, function* () {
                const targetSelectedElement = event.target;
                const targetOptionElement = targetSelectedElement.options[targetSelectedElement.selectedIndex];
                const swimlane_id = parseInt(targetOptionElement.id);
                console.log(`Swimlane selected: text:${this.selectedOption}, id:${swimlane_id}`);
                yield this.select_handler(this.activity_unique_id, swimlane_id);
                yield get_visual_activity_data(window.visual_id);
                plot_visual();
            }));
            if (this.element) {
                this.element.appendChild(select);
            }
        });
    }
}
