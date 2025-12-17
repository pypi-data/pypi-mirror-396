export const name = "LinoParamsPanel";


import React from "react";
import * as constants from './constants';
import { RegisterImportPool, getExReady, URLContextType } from "./Base";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
let ex; const exModulePromises = ex = {
    prButton: import(/* webpackChunkName: "prButton_LinoParamsPanel" */"primereact/button"),
    u: import(/* webpackChunkName: "LinoUtils_LinoParamsPanel" */"./LinoUtils"),
    lc: import(/* webpackChunkName: "LinoComponents_LinoParamsPanel" */"./LinoComponents"),
    i18n: import(/* webpackChunkName: "i18n_LinoParamsPanel" */"./i18n"),
};RegisterImportPool(ex);


export function LinoParamsPanel() {
    const context = React.useContext(URLContextType);
    const ad = context.controller.static.actorData;
    const [ randomKey, setRandomKey ] = React.useState(context.controller.newSlug())
    const [dualParamsPanel, ] = React.useState(
        !!ad.params_layout && !!ad.full_params_layout
    );
    const [ fullParamsPanel, setParamsPanelType ] = React.useState(
        context.fullParamsPanel || false
    );
    const [paramsLayout, setParamsLayout] = React.useState(
        context.fullParamsPanel || !ad.params_layout ? ad.full_params_layout : ad.params_layout
    );
    if (!paramsLayout) return null;

    const localEx = getExReady(ex, ['u', 'lc', 'prButton', 'i18n'], (mods) => {
        mods.i18n = mods.i18n.default;
    });
    return !localEx.ready ? null : <div
        key={randomKey}
        hidden={!context.pvPVisible}
        className="l-params-panel l-header">
        <localEx.lc.LinoLayout
            editing_mode={true}
            window_layout={paramsLayout}
            wt={constants.WINDOW_TYPE_PARAMS}/>
        {dualParamsPanel && <localEx.prButton.Button
            className="l-params-panel-more-button"
            label={fullParamsPanel ? localEx.i18n.t("Less ...") : localEx.i18n.t("More ...")}
            onClick={() => {
                const newFullParamsPanel = !fullParamsPanel;
                setParamsPanelType(newFullParamsPanel);
                setParamsLayout(
                    newFullParamsPanel ? ad.full_params_layout : ad.params_layout
                );
                context.controller.history.replace({fullParamsPanel: newFullParamsPanel});
                setRandomKey(context.controller.newSlug())
            }}
            tooltip={fullParamsPanel
                ? localEx.i18n.t("Show Less Parameters")
                : localEx.i18n.t("Show More Parameters")}
            tooltipOptions={{position: 'bottom'}}/>}
    </div>
}
