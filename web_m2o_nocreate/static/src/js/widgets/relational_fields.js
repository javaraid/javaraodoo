odoo.define('web.relational_fields_no_create', function (require) {
"use strict";

var relational_fields = require('web.relational_fields');
var FieldMany2One = relational_fields.FieldMany2One
FieldMany2One.include({
	init: function (parent, name, record, options) {
		this._super.apply(this, arguments);
		if (this.nodeOptions.no_create === undefined) {
			this.nodeOptions.no_create = true;
		}
		this.can_create = ('can_create' in this.attrs ? JSON.parse(this.attrs.can_create) : true) &&
            !this.nodeOptions.no_create;
	}
});
});
