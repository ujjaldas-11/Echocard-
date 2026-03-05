from django import forms


class FlashcardForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control-dark w-100',
            'placeholder': 'e.g. Biology Chapter 3, World War II...',
        })
    )

    text = forms.CharField(
        required = False,
        widget=forms.Textarea(attrs={
            'class': 'form-control-dark w-100',
            'rows': 10,
            'placeholder': 'Paste your study notes, textbook content, or any text here...',
            }
        )
    )

    pdf_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'd-none',
            'accept': '.pdf',
            'id': 'pdf-file',
        }) 
    )

    num_cards = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=5,
        widget=forms.HiddenInput(attrs={
            'id': 'num-cards-input',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text')
        pdf_file = cleaned_data.get('pdf_file')

        # Must have either text or PDF
        if not text and not pdf_file:
            raise forms.ValidationError(
                'Please provide text or upload a PDF.'
            )
        return cleaned_data

    def clean_pdf_file(self):
        pdf = self.cleaned_data.get('pdf_file')
        if pdf:
            # Validate file type
            if not pdf.name.endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are allowed.')
            # Validate file size (10MB max)
            if pdf.size > 10 * 1024 * 1024:
                raise forms.ValidationError('PDF file must be under 10MB.')
        return pdf

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError('Please provide a deck title.')
        return title

class NoteForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control-dark w-100',
            'placeholder': 'e.g. Chapter 5 Summary, Lecture Notes...',
        })
    )
    text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control-dark w-100',
            'rows': 10,
            'placeholder': 'Paste your text here to generate structured notes...',
        })
    )
    pdf_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'd-none',
            'accept': '.pdf',
            'id': 'pdf-file',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text')
        pdf_file = cleaned_data.get('pdf_file')

        if not text and not pdf_file:
            raise forms.ValidationError(
                'Please provide text or upload a PDF.'
            )
        return cleaned_data

    def clean_pdf_file(self):
        pdf = self.cleaned_data.get('pdf_file')
        if pdf:
            if not pdf.name.endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are allowed.')
            if pdf.size > 10 * 1024 * 1024:
                raise forms.ValidationError('PDF file must be under 10MB.')
        return pdf

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError('Please provide a note title.')
        return title

