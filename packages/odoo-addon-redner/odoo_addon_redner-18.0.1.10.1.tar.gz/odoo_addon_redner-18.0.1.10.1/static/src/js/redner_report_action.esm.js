/*
Redner Odoo module
Copyright © 2016 XCG SAS <https://orbeet.io/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

/* Add a report handler to download redner reports.
 * Adapted from OCA's report_xlsx module:
 * https://github.com/OCA/reporting-engine/blob/18.0/report_xlsx/static/src/js/report/action_manager_report.esm.js
 */

import {download} from '@web/core/network/download';
import {registry} from '@web/core/registry';
import {user} from '@web/core/user';

registry
    .category('ir.actions.report handlers')
    .add('redner_handler', async function (action, options, env) {
        if (action.report_type === 'redner') {
            const type = action.report_type;
            let url = `/report/${type}/${action.report_name}`;
            const actionContext = action.context || {};
            if (action.data && JSON.stringify(action.data) !== '{}') {
                // Build a query string with `action.data` (it's the place where reports
                // using a wizard to customize the output traditionally put their options)
                const action_options = encodeURIComponent(
                    JSON.stringify(action.data)
                );
                const context = encodeURIComponent(
                    JSON.stringify(actionContext)
                );
                url += `?options=${action_options}&context=${context}`;
            } else {
                if (actionContext.active_ids) {
                    url += `/${actionContext.active_ids.join(',')}`;
                }
                if (type === 'redner') {
                    const context = encodeURIComponent(
                        JSON.stringify(user.context)
                    );
                    url += `?context=${context}`;
                }
            }
            env.services.ui.block();
            try {
                await download({
                    url: '/report/download',
                    data: {
                        data: JSON.stringify([url, action.report_type]),
                        context: JSON.stringify(user.context),
                    },
                });
            } finally {
                env.services.ui.unblock();
            }
            const onClose = options.onClose;
            if (action.close_on_report_download) {
                return env.services.action.doAction(
                    {type: 'ir.actions.act_window_close'},
                    {onClose}
                );
            } else if (onClose) {
                onClose();
            }
            return Promise.resolve(true);
        }
        return Promise.resolve(false);
    });
