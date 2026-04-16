
/** @odoo-module */

import { PosStore } from "@point_of_sale/app/services/pos_store";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(PosStore.prototype, {

    async pay() {
        var self = this;
           let order = this.getOrder();
           let lines = order.getOrderlines();
           let pos_config = this.pos;
           let call_super = true;
           var config_id=self.env.services.pos.config.id;
           let prod_used_qty = {};
           let restrict = false;
           if(this.env.services.pos.config.restrict_zero_qty){

             for (let line of lines) {
                   let prd = line.product_id;
                   if (line.qty > 0){
                       let stockquant;
                       if(line.pack_lot_ids[0]?.lot_name){
                            console.log('5555555-----------------if',line.pack_lot_ids[0]?.lot_name)
                            console.log('this.models["stock.quant"]',this.env.services.pos.config.picking_type_id.default_location_src_id.id)
                           stockquant = this.models["stock.quant"].filter(
                            (p) => p.product_id?.id === prd.id &&
                            p.location_id?.id === this.env.services.pos.config.picking_type_id.default_location_src_id.id && p.lot_id?.name === line.pack_lot_ids[0]?.lot_name);
                       console.log('stockquant-----------------if',stockquant)

                       }else{
                           console.log('2425225',this.env.services.pos.config.picking_type_id.default_location_src_id)
                           stockquant = this.models["stock.quant"].filter(
                            (p) => p.product_id?.id === prd.id &&
                            p.location_id?.id === this.env.services.pos.config.picking_type_id.default_location_src_id.id);
                            console.log('stockquant-----------------else',stockquant)

                       }
                       let total_qty = stockquant.reduce((sum, sq) => {
                            return sum + (sq.inventory_quantity_auto_apply || 0);
                        }, 0);

                       console.log('stockquant.inventory_quantity_auto_apply?',total_qty)
                       console.log('stockquant2222',stockquant)
                       if (prd.type == 'consu'){
                           if (stockquant && stockquant.length > 0){
                               if(stockquant[0].id in prod_used_qty){
                                   let old_qty = prod_used_qty[stockquant[0].id][1];
                                   prod_used_qty[stockquant[0].id] = [total_qty,line.qty+old_qty]
                               }else{
                                   prod_used_qty[stockquant[0].id] = [total_qty,line.qty]
                               }
                           }else{
                               if(prd.id in prod_used_qty){
                                   let old_qty = prod_used_qty[prd.id][1];
                                   prod_used_qty[prd.id] = [prd.qty_available,line.qty+old_qty]
                               }else{
                                   prod_used_qty[prd.id] = [prd.qty_available,line.qty]
                               }
                           }

                       }
                       console.log('prod_used_qty',prod_used_qty)

                       if (prd.type == 'consu'){
                           if(stockquant.length === 0  || total_qty <= 0){                                     // prd.qty_available <= 0
                               restrict = true;
                               call_super = false;
                               let lot_name_dis = ''
                               if (line.pack_lot_ids[0]?.lot_name){
                                   lot_name_dis = line.pack_lot_ids[0]?.lot_name
                               }
                               let warning = prd.display_name +' ['+ lot_name_dis +'] is out of stock.';
                               this.dialog.add(AlertDialog, {
                                    title: _t("Zero Quantity Not allowed"),
                                    body: _t(warning),
                                });
                           }

                       }
                   }
             }

                   if(restrict === false){
                   for (let [i, pq] of Object.entries(prod_used_qty)) {
                        console.log('i---------',i)
                        console.log('2233',this.models['stock.quant'])
                        let stk = this.models['stock.quant'].find(q => q.id == i);
                        console.log('stkxxx---------',stk)
                           let check = pq[0] - pq[1];
                           let lot_name_dis = ''
                           if (stk.lot_id){
                               lot_name_dis = stk.lot_id.name
                           }
                           let warning = stk.product_id.display_name +' ['+ lot_name_dis +'] is out of stock.';
                           if (stk.product_id.type == 'consu'){
                               if (check < 0){
                                   call_super = false;
                                    this.dialog.add(AlertDialog, {
                                       title: _t('Deny Order'),
                                       body: _t(warning),
                                   });
                               }
                           }
                    }
                   }
           }
           if(call_super){
               super.pay();
           }
    },

});