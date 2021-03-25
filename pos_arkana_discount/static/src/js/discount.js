odoo.define("pos_arkana_discount.discount", function (require) {
  "use strict";

  var models = require("point_of_sale.models");
  var gui = require("point_of_sale.gui");
  var screens = require("point_of_sale.screens");
  var PopupWidget = require("point_of_sale.popups");

  var core = require("web.core");

  var QWeb = core.qweb;
  var _t = core._t;

  var JavaraGlobalDiscountWidget = PopupWidget.extend({
    template: "JavaraGlobalDiscountWidget",

    show: function (options) {
      this._super(options);
    },

    click_confirm: function () {
      var value = this.$("#disc_type").val();
      var value1 = this.$("#global_disc").val();

      this.gui.close_popup();
      if (this.options.confirm) {
        this.options.confirm.call(this, value, value1);
      }
    },
  });

  gui.define_popup({
    name: "javara_global_discount_widget",
    widget: JavaraGlobalDiscountWidget,
  });

  var GlobalDiscountButton = screens.ActionButtonWidget.extend({
    template: "GlobalDiscountButton",
    init: function (parent, options) {
      this._super(parent, options);

      this.pos.get("orders").bind(
        "add remove change",
        function () {
          this.renderElement();
        },
        this
      );

      this.pos.bind(
        "change:selectedOrder",
        function () {
          this.renderElement();
        },
        this
      );
    },
    button_click: function () {
      var self = this;

      self.gui.show_popup("javara_global_discount_widget", {
        title: _t("Add Global Discount"),
        confirm: function (disc_type, global_disc) {
          var order = self.pos.get_order();
          var lines = order.get_orderlines();

          if (
            order.choose_disc != undefined &&
            order.choose_disc != "global_disc"
          ) {
            self.gui.show_popup("error", {
              title: _t(
                "Global Discount : Discount Already set another discount "
              ),
              body: _t("Please return to the original settings Or Refresh"),
            });
            return;
          }

          if (order.disc_type == "") {
            order.set_choose_disc(undefined);
          }

          if (lines <= 0) {
            order.set_choose_disc(undefined);
            self.gui.show_popup("error", {
              title: _t("Global Discount : Shopping cart is empty"),
              body: _t(
                "Please fill in the Global discount after entering the shopping cart"
              ),
            });
            return;
          }

          order.set_choose_disc("global_disc");
          order.set_global_disc(global_disc, disc_type);
          order.trigger("change");
        },
      });
    },
    // func hitung & update order line
    // global_disc mungkin % atau fix

    get_current_disc_type_name: function () {
      var name_disc_type = _t("Global Disc:");
      var order_disc_type = this.pos.get_order();

      if (order_disc_type) {
        var disc_type_name = order_disc_type.disc_type;

        if (disc_type_name) {
          name_disc_type = disc_type_name;
        }
      }

      return name_disc_type;
    },
    get_current_global_disc_name: function () {
      var name_global_disc = _t(" None");
      var order_global_disc = this.pos.get_order();

      if (order_global_disc) {
        var global_disc_name = order_global_disc.global_disc;

        if (global_disc_name) {
          name_global_disc = global_disc_name;
        }
      }

      return name_global_disc;
    },
  });

  screens.define_action_button({
    name: "global_discount_button",
    widget: GlobalDiscountButton,
    condition: function () {
      return true;
    },
  });

  var _super_order = models.Order.prototype;
  models.Order = models.Order.extend({
    initialize: function () {
      _super_order.initialize.apply(this, arguments);
      if (!this.disc_type) {
        this.disc_type = this.pos.disc_type;
      }

      // % atau fix
      if (!this.global_disc) {
        this.global_disc = this.pos.global_disc;
      }

      // fix
      if (!this.global_disc_amount) {
        this.global_disc_amount = this.pos.global_disc_amount;
      }

      if (!this.choose_disc) {
        this.choose_disc = this.pos.choose_disc;
      }

      this.save_to_db();
    },
    calculate_gloal_disc_line: function (global_disc, disc_type) {
      this.global_disc = global_disc;
      this.disc_type = disc_type;

      var orderLines = this.get_orderlines();
      var summary_price = this.get_total_with_tax();

      if (this.disc_type != "fix") {
        this.global_disc_amount = (summary_price * this.global_disc) / 100;
      } else {
        this.global_disc_amount = this.global_disc;
      }

      for (var i = 0; i < orderLines.length; i++) {
        var line = orderLines[i];

        var global_disc_line = 0;
        var price = line.get_price_with_tax(); //sudah apply discount line
        // hitung disc line
        global_disc_line = (price / summary_price) * this.global_disc_amount;
        // update line
        line.set_global_disc_line(global_disc_line);
      }
    },
    export_as_JSON: function () {
      var json = _super_order.export_as_JSON.apply(this, arguments);
      json.disc_type = this.disc_type ? this.disc_type : "";
      json.global_disc = this.global_disc ? this.global_disc : "";
      json.global_disc_amount = this.global_disc_amount
        ? this.global_disc_amount
        : "";
      json.choose_disc = this.choose_disc ? this.choose_disc : "";
      return json;
    },
    init_from_JSON: function (json) {
      _super_order.init_from_JSON.apply(this, arguments);
      this.disc_type = this.pos.disc_type;
      this.global_disc = this.pos.global_disc;
      this.global_disc_amount = this.pos.global_disc_amount;
      this.choose_disc = this.choose_disc;
    },
    export_for_printing: function () {
      var json = _super_order.export_for_printing.apply(this, arguments);
      json.disc_type = this.disc_type ? this.disc_type : "";
      json.global_disc = this.global_disc ? this.global_disc : "";
      json.global_disc_amount = this.global_disc_amount
        ? this.global_disc_amount
        : "";
      json.choose_disc = this.choose_disc ? this.choose_disc : "";
      return json;
    },
    set_choose_disc: function (choose_disc) {
      this.choose_disc = choose_disc;
      this.trigger("change", this);
    },
    // reset_choose_disc: function (choose_disc) {
    //   var choose_global_disc = choose_disc;
    //   return choose_global_disc;
    // },
    set_global_disc: function (global_disc, disc_type) {
      this.calculate_gloal_disc_line(global_disc, disc_type);
    },
    reset_global_disc: function () {
      this.calculate_gloal_disc_line(0, "");
    },
  });

  var _super_orderline = models.Orderline.prototype;
  models.Orderline = models.Orderline.extend({
    initialize: function (attr, options) {
      _super_orderline.initialize.call(this, attr, options);
      this.global_disc_line = this.global_disc_line;
    },
    set_global_disc_line: function (global_disc_line) {
      this.global_disc_line = global_disc_line;
      this.trigger("change", this);
    },
    get_global_disc_line: function () {
      return this.global_disc_line;
    },
    // get_subtotal: function () {
    //   return round_pr(
    //     this.orderlines.reduce(function (sum, orderLine) {
    //       return sum + (orderLine.get_display_price() - this.global_disc_line);
    //     }, 0),
    //     this.pos.currency.rounding
    //   );
    // },
    // get_total_with_tax: function () {
    //   return (
    //     this.get_total_without_tax() +
    //     this.get_total_tax() -
    //     this.global_disc_line
    //   );
    // },
    export_as_JSON: function () {
      var json = _super_orderline.export_as_JSON.call(this);
      json.global_disc_line = this.global_disc_line;
      return json;
    },
    init_from_JSON: function (json) {
      _super_orderline.init_from_JSON.apply(this, arguments);
      this.global_disc_line = json.global_disc_line;
    },
  });

  screens.OrderWidget.include({
    update_summary: function () {
      this._super();
    },
  });
});
