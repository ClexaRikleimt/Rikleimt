CKEDITOR.dialog.add('translateDialog', function(editor) {
    return {
        title: 'Translate Trigedasleng',
        minWidth: 400,
        minHeight: 200,
        contents: [
            {
                id: 'tab-basic',
                label: 'Translation',
                elements: [
                    {
                        type: 'text',
                        id: 'trig',
                        label: 'Trigedasleng: ',
                        validate: CKEDITOR.dialog.validate.notEmpty("Trigedasleng field cannot be empty"),
                        setup: function(element) {
                            this.setValue(element.getText());
                        },
                        commit: function(element) {
                            element.setText(this.getValue());
                        }
                    },
                    {
                        type: 'text',
                        id: 'translation',
                        label: 'Translation',
                        validate: CKEDITOR.dialog.validate.notEmpty("Translation field cannot be empty"),
                        setup: function(element) {
                            this.setValue(element.getAttribute('data-translation'));
                        },
                        commit: function(element) {
                            element.setAttribute('data-translation', this.getValue())
                        }
                    }
                ]
            },
            {
                id: 'tab-advanced',
                label: 'Advanced settings',
                elements: [
                    {
                        type: 'text',
                        id: 'id',
                        label: 'Id',
                        setup: function(element) {
                            this.setValue(element.getAttribute('id'));
                        },
                        commit: function(element) {
                            var id = this.getValue();
                            if (id) {
                                element.setAttribute('id', id);
                            }
                            else {
                                element.removeAttribute('id');
                            }
                        }
                    }
                ]
            }
        ],
        onShow: function() {
            var selection = editor.getSelection();
            var element = selection.getStartElement();

            var selected_text = selection.getSelectedText();

            if (element) {
                element = element.getAscendant('span', true);
            }

            if (!element || element.getName() !== 'span') {
                element = editor.document.createElement('span');
                element.setText(selected_text);
                element.addClass('translation');
                this.insertMode = true;
            }
            else {
                this.insertMode = false;
            }

            this.element = element;

            this.setupContent(this.element);
        },
        onOk: function() {
            var dialog = this,
                translationElem = dialog.element;

            dialog.commitContent( translationElem );

            if ( dialog.insertMode ) {
                editor.insertElement( translationElem );
            }
        }
    }
});
