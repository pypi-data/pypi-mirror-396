import {patch} from '@web/core/utils/patch';
import {CharField, charField} from '@web/views/fields/char/char_field';

// Adding a new property for dynamic placeholder button visibility
CharField.props = {
    ...CharField.props,
    rednerDynamicPlaceholder: {type: Boolean, optional: true},
    buttonVisibilityField: {type: String, optional: true},
    converterField: {type: String, optional: true},
};

// Extending charField to extract the new property
const charExtractProps = charField.extractProps;
charField.extractProps = (fieldInfo) => {
    return Object.assign(charExtractProps(fieldInfo), {
        rednerDynamicPlaceholder:
            fieldInfo.options?.redner_dynamic_placeholder || false,
        buttonVisibilityField: fieldInfo.options?.button_visibility_field || '',
        converterField: fieldInfo.options?.converter_field || '',
    });
};

// Patching CharField to include the visibility check
patch(CharField.prototype, {
    setup() {
        super.setup();
    },
    get showMagicButton() {
        const visibilityField = this.props.buttonVisibilityField;
        // Return true if no visibility field is configured
        if (!visibilityField) return true;
        return this.props.record.data[visibilityField];
    },
    get hasRednerDynamicPlaceholder() {
        return this.props.rednerDynamicPlaceholder && !this.props.readonly;
    },
    get hasDynamicPlaceholder() {
        return super.hasDynamicPlaceholder && !this.hasRednerDynamicPlaceholder;
    },
    get activeConverterType() {
        return this.props.record.data[this.props.converterField] || '';
    },
    async onDynamicPlaceholderValidate(chain, defaultValue) {
        if (chain) {
            this.input.el.focus();

            // Build placeholder based on converter type
            let placeholder = '';
            switch (this.activeConverterType) {
                case 'field':
                    placeholder = `${chain}`;
                    break;
                // Add other converter types here
                default: {
                    const defaultValuePart = defaultValue?.length
                        ? ` ||| ${defaultValue}`
                        : '';
                    placeholder = `{{object.${chain}${defaultValuePart}}}`;
                    break;
                }
            }
            this.input.el.setRangeText(
                placeholder,
                this.selectionStart,
                this.selectionStart,
                'end'
            );
            // Trigger events to make the field dirty
            this.input.el.dispatchEvent(new InputEvent('input'));
            this.input.el.dispatchEvent(new KeyboardEvent('keydown'));
            this.input.el.focus();
        }
    },
});
