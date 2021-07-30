from odoo.addons.base.models.assetsbundle import AssetsBundle, ScssStylesheetAsset


class AssetsBundleCompanyColor(AssetsBundle):
    def get_company_color_asset_node(self):

        # company_id = self.env["res.company"].search([('id','=',
        #     self.env.context.get("active_company_id", 1))]
        # )
        company_id = (
            self.env.company
            or self.env.user.company_id
        )
        asset = ScssStylesheetAsset(self, url=company_id.scss_get_url())
        compiled = self.compile_css(asset.compile, asset.get_source())
        return ("style", {}, compiled)

