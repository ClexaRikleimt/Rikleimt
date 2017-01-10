CKEDITOR.plugins.add('translation', {
    icons: 'translation',
    init: function(editor) {
        editor.addCommand('translate', new CKEDITOR.dialogCommand('translateDialog', {
            allowedContent: 'span[id,data-translation](translation)'
        }));
        editor.ui.addButton('Translation', {
            label: 'Insert translation (Trigedasleng)',
            command: 'translate',
            toolbar: 'others'
        });

        if (editor.contextMenu) {
            editor.addMenuGroup('translationGroup');
            editor.addMenuItem('translationItem', {
                label: 'Edit translation',
                icon: this.path + 'icons/translation.png',
                command: 'translate',
                group: 'translationGroup'
            });

            editor.contextMenu.addListener(function(element) {
                if (element.getAscendant('span', true)) {
                    return {
                        translationItem: CKEDITOR.TRISTATE_OFF
                    };
                }
            });
        }

        editor.addContentsCss(this.path + 'styles/translation_editor.css');

        CKEDITOR.dialog.add('translateDialog', this.path + 'dialogs/translate.js');
    }
});