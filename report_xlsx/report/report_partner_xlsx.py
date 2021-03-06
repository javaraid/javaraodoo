# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
from xlsxwriter.utility import xl_rowcol_to_cell
from collections import defaultdict

class PartnerXlsx(models.AbstractModel):
    _name = 'report.report_xlsx.partner_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, objects):
        style = {
            'title_bold': workbook.add_format({'bold': True, 'align': 'left', 'text_wrap': False, 'font_size': 13}),
            'normal_bold': workbook.add_format({'bold': True, 'border': True, 'align': 'left', 'text_wrap': True}),
            'title_small': workbook.add_format({'bold': True, 'align': 'center', 'text_wrap': True, 'font_size': 13}),
            'title': workbook.add_format({'bold': True, 'border': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True}),
            'title_financial': workbook.add_format({'font_color': '#16365c', 'font_size': '28', 'bold': True, 'border': True, 'align': 'center', 'text_wrap': True}),
            'title_table': workbook.add_format({'bg_color': '#1f497d', 'font_color': '#ffffff', 'bold': True, 'border': True, 'align': 'center', 'text_wrap': True}),
            'blue': workbook.add_format({'bg_color': '#ccffff', 'bold': True, 'border': True, 'num_format': '#,##0'}),
            'blue_percent': workbook.add_format({'bg_color': '#ccffff', 'bold': True, 'border': True, 'num_format': '0.0%'}),
            'blue_center': workbook.add_format({'bg_color': '#ccffff', 'align': 'center', 'bold': True, 'border': True}),
            'yellow': workbook.add_format({'bg_color': '#ffffcc', 'bold': True, 'border': True, 'num_format': '#,##0'}),
            'yellow_center': workbook.add_format({'bg_color': '#ffffcc', 'align': 'center', 'bold': True, 'border': True}),
            'yellow_right': workbook.add_format({'bg_color': '#ffffcc', 'align': 'right', 'bold': True, 'border': True, 'num_format': '#,##0'}),
            'yellow_percent': workbook.add_format({'bg_color': '#ffffcc', 'bold': True, 'border': True, 'num_format': '0.0%'}),
            'grey': workbook.add_format({'bg_color': '#c0c0c0', 'bold': True, 'border': True, 'num_format': '#,##0'}),
            'normal': workbook.add_format({'border': True, 'num_format': '#,##0', 'text_wrap': True}),
            'normal_border': workbook.add_format({'border': True, 'align': 'left', 'text_wrap': True}),
            'normal_right': workbook.add_format({'border': True, 'num_format': '#,##0.00', 'bold': False, 'align': 'right'}),
            'normal_bold_right': workbook.add_format({'border': True, 'num_format': '#,##0.00', 'bold': True, 'align': 'right'}),
            'normal_bold_right_thick': workbook.add_format({'border': 2, 'num_format': '#,##0.00', 'bold': True, 'align': 'right'}),
            'normal_red': workbook.add_format({'border': True, 'num_format': '#,##0', 'bg_color': 'red'}),
            # 'normal_bold': workbook.add_format({'bold': True, 'border': True, 'num_format': '#,##0'}),
            'normal_bold_noborder': workbook.add_format({'bold': True, 'num_format': '#,##0'}),
            'normal_date': workbook.add_format({'bold': True}),
            'normal_center': workbook.add_format({'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 2, 'bold': True}),
            'normal_vcenter': workbook.add_format({'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'border': True, 'bold': True}),
            'normal_center_noborder': workbook.add_format({'align': 'center', 'border': False}),
            'normal_italic': workbook.add_format({'italic': True, 'border': True}),
            'normal_percent': workbook.add_format({'num_format': '0.0%', 'border': True}),
            'normal_percent_bold': workbook.add_format({'num_format': '0.0%', 'bold': True, 'border': True}),
            'index': workbook.add_format({'num_format': '#', 'align': 'center', 'border': True}),
        }
        row = 4
        col = 1
        for obj in objects:
            sheet = workbook.add_worksheet('Report')
            sheet.panes_frozen = True
            sheet.remove_splits = True
            sheet.portrait = 0
            sheet.fit_width_to_pages = 1
            sheet.freeze_panes(5, 0)
            
            sheet.merge_range('B2:D2', 'REKAPITULASI PIUTANG DAGANG', style['title_bold'])
            sheet.write('B3', 'Tanggal: %s - %s' % (objects['date_from'], objects['date_to']))
            sheet.write(row, col, 'Customer', style['normal_center'])
            sheet.write(row, col+1, 'Saldo Awal \n (A)', style['normal_center'])
            sheet.write(row, col+2, 'Penambahan \n (B)', style['normal_center'])
            sheet.write(row, col+3, 'Cash / Bank \n (C)', style['normal_center'])
            sheet.write(row, col+4, 'Others /  Down Payment \n (D)', style['normal_center'])
            sheet.write(row, col+5, 'Retur \n (E)', style['normal_center'])
            sheet.write(row, col+6, 'Potongan Pembayaran \n (F)', style['normal_center'])
            sheet.write(row, col+7, 'Selisih Kurs \n (G)', style['normal_center'])
            sheet.write(row, col+8, 'Saldo Akhir \n (A+B-C-D-E-F-G)', style['normal_center'])
            sheet.set_column('B2:D2', 15)
            sheet.set_column('C:C', 15.5)
            sheet.set_column('D:D', 15.5)
            sheet.set_column('E:E', 15.5)
            sheet.set_column('F:F', 15.5)
            sheet.set_column('G:G', 15.5)
            sheet.set_column('H:H', 15.5)
            sheet.set_column('I:I', 15.5)
            sheet.set_column('J:J', 15.5)
            sheet.set_row(4, 33)

            # Kolom Saldo Awal
            # get all AR befor date_start
            self.env.cr.execute("""
                select distinct 
                    aml.partner_id, 
                    saldo.bal 
                from 
                    account_move_line as aml 
	            left join (
                    select 
                        partner_id, 
                        sum(balance) as bal 
                    from 
                        account_move_line 
                    where 
                        (account_id = 1928 or account_id = 1929)
                        and date < '%s'
                    group by partner_id
                ) as saldo 
                on 
                    saldo.partner_id = aml.partner_id
	            where 
                    account_id = 1928 or account_id = 1929
                """ % objects['date_from'])
            saldo_awal = dict(self.env.cr.fetchall())
            
            # Kolom Penambahan
            # unused because it is hard to create query for True AR (not from false CN, and other journals)
            self.env.cr.execute("""
                select 
            	rp.id,
            	sum(aml.bal)
            from 
            	res_partner rp
            	left join(
            		select 	
            			aml.partner_id, 
            			sum(aml.balance) as bal
            		from 
            			account_move_line aml
            			join account_journal aj on aj.id = aml.journal_id and aj."type" = 'sale'
            		where
            			(aml.account_id = 1928 or aml.account_id = 1929)
                        and aml.date >= '%s'
                        and aml.date <= '%s'
            		group by
            			aml.partner_id
            		) aml on aml.partner_id = rp.id 
            where 
            	rp.id in (select partner_id from account_move_line where account_id = 1928 or account_id = 1929 group by partner_id)
            group by
            	rp.id;  
            """ % (objects['date_from'], objects['date_to']))
            penambahan = dict(self.env.cr.fetchall())

            # Kolom Cash/Bank
            # get all AR from cash/bank journals
            self.env.cr.execute("""
                select 
                	rp.id,
                	sum(aml.bal)
                from 
                	res_partner rp
                	left join(
                		select 	
                			aml.partner_id, 
                			sum(aml.balance) as bal
                		from 
                			account_move_line aml
                			join account_journal aj on aj.id = aml.journal_id and (aj."type" = 'bank' or aj."type" = 'cash') 
                		where
                            (aml.account_id = 1928 or aml.account_id = 1929)
                			and aml.date >= '%s' 
                            and aml.date <= '%s'  
                		group by
                			aml.partner_id
                		) aml on aml.partner_id = rp.id 
                where 
                	rp.id in (select partner_id from account_move_line where account_id = 1928 or account_id = 1929 group by partner_id)
                group by
                	rp.id;
            """ % (objects['date_from'], objects['date_to']))
            bank = dict(self.env.cr.fetchall())

            product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
            rec_product_id = int(product_id)
            
            # Kolom Others/DP
            # get all Uninvoiced Revenue with DP product
            self.env.cr.execute("""
            select 
            	rp.id,
            	sum(aml.bal)
            from 
            	res_partner rp
            	left join(
            		select 	
            			aml.partner_id, 
            			sum(aml.credit) as bal
            		from 
            			account_move_line aml
            		where 
                        aml.product_id = %d
            			and aml.date >= '%s' 
            			and aml.date <= '%s' 
            		group by
            			aml.partner_id
            		) aml on aml.partner_id = rp.id 
            where 
            	rp.id in (select partner_id from account_move_line where account_id = 1989 or account_id = 2254 group by partner_id)
            group by
            	rp.id;
            """ % (rec_product_id, objects['date_from'], objects['date_to']))
            dp = dict(self.env.cr.fetchall())
                
            # Kolom Retur
            # get all AR from CN with different amount from its invoice (Add CN from Invoice) and CN without invoice (Create CN from list)
            self.env.cr.execute("""
            select 
            	rp.id,
            	sum(aml.bal)
            from 
            	res_partner rp
            	left join(
            		select 	
            			aml.partner_id, 
            			sum(aml.balance) as bal
            		from 
            			account_move_line aml
                        join (
                            select
                                cn.*
                            from
                                account_invoice cn
                                join account_invoice ai on cn.refund_invoice_id = ai.id and cn.amount_total != ai.amount_total
                            where
                                cn.type = 'out_refund' and
                                (cn.state = 'open' or cn.state = 'paid')
                            union
                            select 
                                *
                            from
                                account_invoice
                            where
                                type = 'out_refund' and
                                refund_invoice_id is null and
                                (state = 'open' or state = 'paid')
                        ) credit_note on credit_note.id = aml.invoice_id
            		where
            			(aml.account_id = 1928 or aml.account_id = 1929)
                        and aml.date >= '%s'
                        and aml.date <= '%s'
            		group by
            			aml.partner_id
            		) aml on aml.partner_id = rp.id 
            where 
            	rp.id in (select partner_id from account_move_line where account_id = 1928 or account_id = 1929 group by partner_id)
            group by
            	rp.id;
            """ % (objects['date_from'], objects['date_to']))
            retur = dict(self.env.cr.fetchall())

            # Kolom Pemotongan Pembayaran
            # get all AR from In-store promo journal
            self.env.cr.execute("""
            select 
            	rp.id,
            	sum(aml.bal)
            from 
            	res_partner rp
            	left join(
            		select 	
            			aml.partner_id, 
            			sum(aml.balance) as bal
            		from 
            			account_move_line aml
            		where
                        (aml.account_id = 1928 or aml.account_id = 1929) 
                        and aml.journal_id = 23
            			and aml.date >= '%s' 
            			and aml.date <= '%s' 
            		group by
            			aml.partner_id
            		) aml on aml.partner_id = rp.id 
            where 
            	rp.id in (select partner_id from account_move_line where account_id = 1928 or account_id = 1929 group by partner_id)
            group by
            	rp.id;
            """ % (objects['date_from'], objects['date_to']))
            pp = dict(self.env.cr.fetchall())

            # Kolom Selisih Kurs
            # get all AR from Exchange Difference journal
            self.env.cr.execute("""
            select 
            	rp.id,
            	sum(aml.bal)
            from 
            	res_partner rp
            	left join(
            		select 	
            			aml.partner_id, 
            			sum(aml.balance) as bal
            		from 
            			account_move_line aml
            		where
                        (aml.account_id = 1928 or aml.account_id = 1929) 
                        and aml.journal_id = 3
            			and aml.date >= '%s' 
            			and aml.date <= '%s' 
            		group by
            			aml.partner_id
            		) aml on aml.partner_id = rp.id 
            where 
            	rp.id in (select partner_id from account_move_line where account_id = 1928 or account_id = 1929 group by partner_id)
            group by
            	rp.id;
            """ % (objects['date_from'], objects['date_to']))
            exch_diff = dict(self.env.cr.fetchall())

            # Kolom Saldo Akhir
            # get all AR up to date_end
            self.env.cr.execute("""
            select distinct 
                aml.partner_id, 
                saldo.bal 
            from 
                account_move_line as aml 
	        left join (
                select 
                    partner_id, 
                    sum(balance) as bal 
                from 
                    account_move_line 
                where 
                    (account_id = 1928 or account_id = 1929) 
                    and date <= '%s'
                group by partner_id
            ) as saldo 
            on 
                saldo.partner_id = aml.partner_id
	        where 
                account_id = 1928 or account_id = 1929;
            """ % objects['date_to'])
            saldo_akhir = dict(self.env.cr.fetchall())
            
            res = defaultdict(lambda:{
                'saldo_awal':0, 'penambahan':0, 'bank':0, 'dp':0, 'retur':0, 'pp':0, 'exch_diff':0, 'saldo_akhir':0})
            
            for p_id, values in saldo_awal.items() :
                if not values: values = 0
                res[p_id]['saldo_awal'] += values            
            for p_id, values in penambahan.items():
                if not values: values = 0
                res[p_id]['penambahan'] += values
            for p_id, values in bank.items():
                if not values: values = 0
                res[p_id]['bank'] += values
            for p_id, values in dp.items():
                if not values: values = 0
                res[p_id]['dp'] += values
            for p_id, values in retur.items():
                if not values: values = 0
                res[p_id]['retur'] += values
            for p_id, values in pp.items():
                if not values: values = 0
                res[p_id]['pp'] += values
            for p_id, values in exch_diff.items():
                if not values: values = 0
                res[p_id]['exch_diff'] += values
            for p_id, values in saldo_akhir.items():
                if not values: values = 0
                res[p_id]['saldo_akhir'] += values

            teams = self.env['crm.team'].search([])
            pp = 0
            value = []
            gt_saldo_awal = 0
            gt_saldo_akhir = 0
            gt_penambahan = 0
            gt_bank = 0
            gt_dp = 0
            gt_retur = 0
            gt_pp = 0
            gt_exch_diff = 0
            
            for team in teams:
                partners = self.env['res.partner'].search([
                            ('team_id', '=', team.id),
                            ('customer', '=', True),
                        ])
                # cell_merge_sales_channel1 = xl_rowcol_to_cell(row+1, col)
                # cell_merge_sales_channel2 = xl_rowcol_to_cell(row+1, col+7)

                # sheet.merge_range(
                #     cell_merge_sales_channel1 + ':' + cell_merge_sales_channel2, team.name, style['normal_bold'])
                
                row_start = row+1   
                idx = 0
                print_total = False

                for rec in res:
                    # Kondisi Pengisian Kolom
                    partner_value = res[rec]['saldo_awal'] or res[rec]['penambahan'] or res[rec]['bank'] or res[rec]['dp'] or res   [rec]['retur'] or res[rec]['pp'] or res[rec]['exch_diff'] or res[rec]['saldo_akhir']

                    # import ipdb; ipdb.set_trace()
                    # Format Sum Saldo Akhir 
                    # Kolom Customer                
                    partner = self.env['res.partner'].browse(rec)    

                    if rec in partners.ids:                        
                        if partner_value :
                            if idx == 0:
                                print_total = True
                                cell_merge_sales_channel1 = xl_rowcol_to_cell(row+1, col)
                                cell_merge_sales_channel2 = xl_rowcol_to_cell(row+1, col+8)
                                sheet.set_row(row+1, 23)      
                                sheet.merge_range(cell_merge_sales_channel1 + ':' + cell_merge_sales_channel2, team.name, style['normal_vcenter'])
                                idx+=1
                                row+=1

                            sheet.write(row+1, col, partner.name, style['normal_border']) 
                            sheet.write(row+1, col+1, res[rec]['saldo_awal'], style['normal_right']) 
                            sheet.write(row+1, col+2, res[rec]['penambahan'] - res[rec]['dp'] - res[rec]['retur'] - res[rec]['pp'], style['normal_right'])
                            sheet.write(row+1, col+3, res[rec]['bank']*-1, style['normal_right'])
                            sheet.write(row+1, col+4, res[rec]['dp']*-1, style['normal_right'])
                            sheet.write(row+1, col+5, res[rec]['retur']*-1, style['normal_right'])
                            sheet.write(row+1, col+6, res[rec]['pp']*-1, style['normal_right'])
                            sheet.write(row+1, col+7, res[rec]['exch_diff']*-1, style['normal_right'])
                            sheet.write(row+1, col+8, res[rec]['saldo_akhir'], style['normal_right'])
                            
                            # cell_saldo_awal = xl_rowcol_to_cell(row+1, col+1)
                            # cell_penambahan = xl_rowcol_to_cell(row+1, col+2)
                            # cell_bank = xl_rowcol_to_cell(row+1, col+3)
                            # cell_dp = xl_rowcol_to_cell(row+1, col+4)
                            # cell_retur = xl_rowcol_to_cell(row+1, col+5)
                            # cell_saldo_akhir = xl_rowcol_to_cell(row+1, col+7)
                            # sheet.write(
                            #     row+1, col+6, '=' +
                            #     cell_saldo_awal + '+' + cell_penambahan + '-' + 
                            #     cell_bank + '-' + cell_dp + '-' + 
                            #     cell_retur + '-' + cell_saldo_akhir, 
                            #     style['normal_right']
                            # )
                            # cell_merge_sales_channel1 = xl_rowcol_to_cell(row_title, col)
                            # cell_merge_sales_channel2 = xl_rowcol_to_cell(row_title, col+7)
                            # sheet.merge_range(
                            #     cell_merge_sales_channel1 + ':' + cell_merge_sales_channel2, team.name, style['normal_bold'])
                            row+=1
                            
                            gt_saldo_awal += res[rec]['saldo_awal']         
                            gt_penambahan += res[rec]['penambahan']         
                            gt_bank += res[rec]['bank']         
                            gt_dp += res[rec]['dp']
                            gt_retur += res[rec]['retur']         
                            gt_pp += res[rec]['pp']         
                            gt_exch_diff += res[rec]['exch_diff']
                            gt_saldo_akhir += res[rec]['saldo_akhir']
                         
                
                cell_col_saldo_awal_1 = xl_rowcol_to_cell(row, col+1)
                cell_col_saldo_awal_2 = xl_rowcol_to_cell(row_start, col+1)
                cell_penambahan_1 = xl_rowcol_to_cell(row, col+2)
                cell_penambahan_2 = xl_rowcol_to_cell(row_start, col+2)
                cell_bank_1 = xl_rowcol_to_cell(row, col+3)
                cell_bank_2 = xl_rowcol_to_cell(row_start, col+3)
                cell_dp_1 = xl_rowcol_to_cell(row, col+4)
                cell_dp_2 = xl_rowcol_to_cell(row_start, col+4)
                cell_retur_1 = xl_rowcol_to_cell(row, col+5)
                cell_retur_2 = xl_rowcol_to_cell(row_start, col+5)
                cell_pp_1 = xl_rowcol_to_cell(row, col+6)
                cell_pp_2 = xl_rowcol_to_cell(row_start, col+6)
                cell_exch_1 = xl_rowcol_to_cell(row, col+7)
                cell_exch_2 = xl_rowcol_to_cell(row_start, col+7)
                cell_total_1 = xl_rowcol_to_cell(row, col+8)
                cell_total_2 = xl_rowcol_to_cell(row_start, col+8)    
                
                if print_total:
                    sheet.write(row+1, col, "Total %s " % team.name, style['normal_center'])
                    sheet.write(row+1, col+1, '=SUM(' + cell_col_saldo_awal_1 + ':' + cell_col_saldo_awal_2 + ')', style['normal_bold_right_thick'])
                    sheet.write(row+1, col+2, '=SUM(' + cell_penambahan_1 + ':' + cell_penambahan_2 + ')', style['normal_bold_right_thick'])
                    sheet.write(row+1, col+3, '=SUM(' + cell_bank_1 + ':' + cell_bank_2 + ')', style['normal_bold_right_thick'])
                    sheet.write(row+1, col+4, '=SUM(' + cell_dp_1 + ':' + cell_dp_2 + ')', style['normal_bold_right_thick'])
                    sheet.write(row+1, col+5, '=SUM(' + cell_retur_1 + ':' + cell_retur_2 + ')', style['normal_bold_right_thick'])
                    sheet.write(row+1, col+6, '=SUM(' + cell_pp_1 + ':' + cell_pp_2 + ')', style['normal_bold_right_thick'])
                    sheet.write(row+1, col+7, '=SUM(' + cell_exch_1 + ':' + cell_exch_2 + ')', style['normal_bold_right_thick'])
                    value.append((row+1, col+7))
                    sheet.write(row+1, col+8, '=SUM(' + cell_total_1 + ':' + cell_total_2 + ')', style['normal_bold_right_thick'])
                    row+=1

            sheet.set_row(row+1, 23)
            sheet.write(row+1, col, "Grand Total", style['normal_center'])    
            sheet.write(row+1, col+1, gt_saldo_awal, style['normal_bold_right_thick'])
            sheet.write(row+1, col+2, gt_penambahan - gt_dp - gt_retur - gt_pp, style['normal_bold_right_thick'])
            sheet.write(row+1, col+3, gt_bank*-1, style['normal_bold_right_thick'])
            sheet.write(row+1, col+4, gt_dp*-1, style['normal_bold_right_thick'])
            sheet.write(row+1, col+5, gt_retur*-1, style['normal_bold_right_thick'])
            # new_value = []
            # for coor in value:
            #     coor_string = xl_rowcol_to_cell(coor[0], coor[1])
            #     new_value.append(coor_string)

            # value = [xl_rowcol_to_cell(coor[0], coor[1]) for coor in value]
            # pp_value = '=' + '+'.join(value)

            sheet.write(row+1, col+6, gt_pp*-1, style['normal_bold_right_thick'])
            sheet.write(row+1, col+7, gt_exch_diff*-1, style['normal_bold_right_thick'])
            sheet.write(row+1, col+8, gt_saldo_akhir, style['normal_bold_right_thick'])
                    
            # '=SUM(' + xl_rowcol_to_cell(row+1, col+1) + ':' + xl_rowcol_to_cell(row+1, col+6) + ')'
            # get all sales channel
            # for all sales channel
                # cari semua customer utk 1 sales channel
                # perhitungan value pake sql, modelnya account.move.line

            

    
