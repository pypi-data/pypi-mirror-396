###
# Form field classes are used for grouping, ordering and laying out fields.
###


class Field:
    """
    Field class for configuring the fields in content edit views in Django Content Studio.
    """

    def __init__(self, name: str, col_span: int = 1, label: str = None):
        self.name = name
        self.col_span = col_span
        self.label = label

    def serialize(self):
        return {
            "name": self.name,
            "col_span": self.col_span,
            "label": self.label,
        }


class FieldLayout:
    """
    Field layout class for configuring the layout of fields in content edit views in Django Content Studio.
    """

    def __init__(self, fields: list[str | Field] = None, columns: int = 1):
        self.fields = [self._normalize_field(f) for f in fields] if fields else []
        self.columns = columns

    def serialize(self):
        return {
            "fields": [field.serialize() for field in self.fields],
            "columns": self.columns,
        }

    def _normalize_field(self, field):
        if isinstance(field, str):
            return Field(field)
        elif isinstance(field, Field):
            return field
        else:
            raise ValueError(f"Invalid field: {field}. Must be a string or Field.")


class FormSet:
    """
    Formset class for configuring the blocks of fields in content edit views
    in Django Content Studio.
    """

    def __init__(
        self,
        title: str = "",
        description: str = "",
        fields: list[str | Field | FieldLayout] = None,
    ):
        self.title = title
        self.description = description
        self.fields = [self._normalize_field(f) for f in fields] if fields else []

    def serialize(self):
        return {
            "title": self.title,
            "description": self.description,
            "fields": [field.serialize() for field in self.fields],
        }

    def _normalize_field(self, field):
        if isinstance(field, str):
            return Field(field)
        elif isinstance(field, Field):
            return field
        elif isinstance(field, FieldLayout):
            return field
        else:
            raise ValueError(
                f"Invalid field: {field}. Must be a string, Field or FieldLayout."
            )


class FormSetGroup:
    """
    Formset group class for configuring the groups of form sets in content edit views.
    """

    def __init__(self, label: str = "", formsets: list[FormSet] = None):
        self.label = label
        self.formsets = formsets or []

    def serialize(self):
        return {
            "label": self.label,
            "formsets": [formset.serialize() for formset in self.formsets],
        }
