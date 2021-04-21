odoo.define("pos_arkana_discount_bank.discount", function (require) {
  "use strict";

  var models = require("point_of_sale.models");
  var screens = require("point_of_sale.screens");
  var core = require("web.core");

  var QWeb = core.qweb;
  var _t = core._t;

  // Bank Discount
  var DiscountBankButton = screens.ActionButtonWidget.extend({
    template: "DiscountBankButton",

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

      var no_bank_discount = [
        {
          label: _t("None"),
        },
      ];
      var bank_discounts = _.map(
        self.pos.bank_discounts,
        function (bank_discount) {
          return {
            label: bank_discount.name,
            item: bank_discount,
          };
        }
      );

      var selection_list = no_bank_discount.concat(bank_discounts);
      self.gui.show_popup("selection", {
        title: _t("Select Bank Discount"),
        list: selection_list,
        confirm: function (bank_discount) {
          var order = self.pos.get_order();
          order.bank_discount_id = bank_discount;

          if (
            order.choose_disc != undefined &&
            order.choose_disc != "disc_bank"
          ) {
            self.gui.show_popup("error", {
              title: _t(
                "Bank Discount : Discount Already set another discount "
              ),
              body: _t("Please return to the original settings Or Refresh"),
            });
            return;
          }

          order.set_choose_disc("disc_bank");

          var lines = order.get_orderlines();

          if (lines <= 0) {
            self.gui.show_popup("error", {
              title: _t("Bank Discount : Shopping cart is empty"),
              body: _t(
                "Please fill in the Bank discount after entering the shopping cart"
              ),
            });
            return;
          }

          if (order.bank_discount_id == undefined) {
            order.set_choose_disc(undefined);
            var lines = order.get_orderlines();

            var k = 0;
            while (k < lines.length) {
              if (lines[k].get_flag_disc() === "disc_bank") {
                order.remove_orderline(lines[k]);
              } else {
                k++;
              }
            }
          }

          self.apply_bank_discount();
          order.trigger("change");
        },
        is_selected: function (bank_discount) {
          return bank_discount === self.pos.get_order().bank_discount_id;
        },
      });
    },
    apply_bank_discount: function () {
      // var self = this;
      var order = this.pos.get_order();
      var lines = order.get_orderlines();

      if (order.bank_discount_id === undefined) {
        var name = "Bank Discount: None";
        return name;
      }

      var product = this.pos.db.get_product_by_id(
        order.bank_discount_id.product_disc_bank_id[0]
      );

      if (product === undefined) {
        this.gui.show_popup("error", {
          title: _t("No discount product found"),
          body: _t(
            "The discount product seems misconfigured. Make sure it is flagged as 'Can be Sold' and 'Available in Point of Sale'."
          ),
        });
        return;
      }

      // Remove existing product Bank
      var i = 0;
      while (i < lines.length) {
        if (
          lines[i].get_product() === product ||
          lines[i].get_flag_disc() === "disc_bank"
        ) {
          order.remove_orderline(lines[i]);
        } else {
          i++;
        }
      }

      var nilai_pos = order.get_total_with_tax();
      // console.log(nilai_pos);
      var min_trans = this.pos.get_order().bank_discount_id.min_amount;
      // console.log(min_trans);
      var max_trans = this.pos.get_order().bank_discount_id.max_amount;
      // console.log(max_trans);
      var disc_bank = 0;
      if (nilai_pos < min_trans) {
        order.set_choose_disc(undefined);
        this.pos.gui.show_popup("error", {
          title: _t("Transaction cannot be continued"),
          body: _t("Please Change Discount Bank"),
        });
        return;
      }

      if (min_trans < nilai_pos && nilai_pos < max_trans) {
        var disc_bank_percernt = this.pos.get_order().bank_discount_id
          .disc_percent;
        disc_bank = (disc_bank_percernt / 100.0) * nilai_pos;
        // console.log(disc_bank, "percent");
      }

      if (nilai_pos > max_trans) {
        var disc_bank = this.pos.get_order().bank_discount_id.disc_amount;
        // console.log(disc_bank, "rp");
      }

      // console.log(product);
      if (disc_bank > 0) {
        var price = -disc_bank;
        var flag = "disc_bank";
        order.add_product(product, {
          price: price,
          extras: { flag_disc: flag },
        });
      }
    },
    get_current_bank_discount_name: function () {
      var name = _t("Bank Discount: None");
      var order = this.pos.get_order();

      if (order) {
        var bank_discount = order.bank_discount_id;

        if (bank_discount) {
          name = bank_discount.name;
        }
      }

      if (order.choose_disc != "disc_bank") {
        name = _t("Bank Discount: None");
      }

      return name;
    },
  });

  screens.define_action_button({
    name: "bank_discount",
    widget: DiscountBankButton,
    condition: function () {
      return true;
    },
  });

  // load model
  models.load_models({
    model: "pos.discount.bank",
    fields: [
      "name",
      "product_disc_bank_id",
      "min_amount",
      "max_amount",
      "disc_amount",
      "disc_percent",
    ],
    //domain: function(self){ return [['pos_config_id','=',self.config.id]]; },
    loaded: function (self, bank_discounts) {
      self.bank_discounts = bank_discounts;
      self.bank_discounts_by_id = {};
      for (var i = 0; i < bank_discounts.length; i++) {
        self.bank_discounts_by_id[bank_discounts[i].id] = bank_discounts[i];
      }
    },
  });

  var _super = models.Order;
  models.Order = models.Order.extend({
    export_as_JSON: function () {
      var json = _super.prototype.export_as_JSON.apply(this, arguments);
      json.bank_discount_id = this.bank_discount_id
        ? this.bank_discount_id.id
        : false;
      json.choose_disc = this.choose_disc ? this.choose_disc : "";
      return json;
    },
    set_choose_disc: function (choose_disc) {
      this.choose_disc = choose_disc;
      this.trigger("change", this);
    },
  });

  var _super_orderline = models.Orderline.prototype;
  models.Orderline = models.Orderline.extend({
    initialize: function (attr, options) {
      _super_orderline.initialize.call(this, attr, options);
      this.flag_disc = this.flag_disc;
    },
    get_flag_disc: function () {
      return this.flag_disc;
    },
    export_as_JSON: function () {
      var json = _super_orderline.export_as_JSON.call(this);
      json.flag_disc = this.flag_disc;
      return json;
    },
    init_from_JSON: function (json) {
      _super_orderline.init_from_JSON.apply(this, arguments);
      this.flag_disc = json.flag_disc;
    },
  });
});
