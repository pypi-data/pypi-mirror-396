import * as t from '../../types';
import * as constants from "../../constants";
import { setTimeout } from "timers/promises";


describe("noi/URLContext.ts", () => {
    let page;

    beforeAll(async () => {
        page = await globalThis.__BROWSER_GLOBAL__.newPage();
        // page.on("console", message => console.log(message.text()));
        await global.wait.runserverInit();
        await page.setDefaultNavigationTimeout(0);
    });

    beforeEach(async () => {
        await page.goto(global.SERVER_URL);
        await page.waitForNetworkIdle();
        await global.signIn(page);
    });

    afterAll(async () => {
        await page.close();
    });

    it('Getting focus on the first input element in an action window', async () => {
        await page.evaluate((c) => {
            window.App.URLContext.history.pushPath({
                pathname: "/api/tickets/AllTickets",
                params: {
                    [c.URL_PARAM_DISPLAY_MODE]: c.DISPLAY_MODE_TABLE,
                }
            })
        }, constants);
        await page.waitForNetworkIdle();

        await page.keyboard.press("Insert");
        await setTimeout(500);

        const summary = "Test ticket summary";
        await page.keyboard.type(summary);

        const carriedSummary = await page.evaluate((c) => {
            return (Object.values(window.App.URLContext.children).filter(
                (ctx: t.NavigationContext) => ctx.contextType === c.CONTEXT_TYPE_ACTION
            )[0] as t.NavigationContext).dataContext.mutableContext.data.summary;
        }, constants);

        expect(summary).toEqual(carriedSummary);
        
        await page.evaluate((c) => {
            (Object.values(window.App.URLContext.children).filter(
                (ctx: t.NavigationContext) => ctx.contextType === c.CONTEXT_TYPE_ACTION
            )[0] as t.NavigationContext).actionHandler.clearMod();
        }, constants);
        await page.keyboard.press("Escape");
        await setTimeout(200);

        await page.evaluate(() => {
            const { URLContext } = window.App;
            URLContext.actionHandler.singleRow({}, URLContext.dataContext.mutableContext.rows[0][
                URLContext.static.actorData.pk_index]);
        });
        await page.waitForNetworkIdle();

        await page.evaluate(() => {
            const { URLContext } = window.App;
            (Object.values(URLContext.children)[0] as t.NavigationContext)
                .actionHandler.copyContext(URLContext);
        });
        await page.waitForNetworkIdle();
        
        await page.keyboard.press("Insert");
        await setTimeout(500);

        const body = "Test ticket body";
        await page.keyboard.type(body);

        const carriedBody = await page.evaluate((c) => {
            return (Object.values(window.App.URLContext.children).filter(
                (ctx: t.NavigationContext) => ctx.contextType === c.CONTEXT_TYPE_ACTION
            )[0] as t.NavigationContext).dataContext.mutableContext.data.body;
        }, constants);

        expect(carriedBody).toEqual(`<p>${body}</p>`);

        await page.evaluate(() => {
            window.App.URLContext.actionHandler.clearMod();
        });
        await page.keyboard.press("Escape");
    });

    it("Inserting decimals in a NumberInput", async () => {
        await page.evaluate(() => {
            window.App.state.menu_data.filter(
                md => md.label === 'Sales'
            )[0].items.filter(
                md => md.label === 'Sales invoices (SLS)'
            )[0].command();
        });
        await page.waitForNetworkIdle();

        await page.evaluate(() => {
            const { URLContext } = window.App;
            URLContext.actionHandler.singleRow(
                {}, URLContext.dataContext.mutableContext.pks[0]);
        });
        await page.waitForNetworkIdle();
        
        await page.locator("div>span>a::-p-text(Draft)").click();
        await page.waitForNetworkIdle();

        await page.evaluate(() => {
            const { URLContext } = window.App;
            const childContext = (Object.values(URLContext.children)[0] as t.NavigationContext);
            childContext.actionHandler.singleRow(
                {},
                childContext.dataContext.mutableContext.pks[0],
                URLContext
            );
        });
        await page.waitForNetworkIdle();

        await page.evaluate(() => {
            window.App.URLContext.history.replace({
                editing_mode: true,
            });
        });

        typeToElement("1234.56", "label ::-p-text(Discount rate)", "input");
        await setTimeout(500);  // wait for debounce

        const discountRate = await page.evaluate(() => {
            return window.App.URLContext.dataContext.mutableContext.data.discount_rate;
        });
        
        expect(discountRate).toBe(1234.56);

        await page.evaluate(() => {
            window.App.URLContext.actionHandler.clearMod();
        });

        await page.goBack();
        await page.waitForNetworkIdle();

        await page.locator("div>span>a::-p-text(Registered)").click();
        await page.waitForNetworkIdle();
    });

    it("Multi row selected delete", async () => {
        await page.evaluate(() => {
            window.App.URLContext.history.pushPath({
                pathname: "/api/tickets/AllTickets"
            });
        });
        await page.waitForNetworkIdle();

        const newTickets = [];

        await createTicket("test ticket 1");

        // eslint-disable-next-line no-var
        var {rowPK, headerTitle} = await pkAndTitle();
        expect(headerTitle).toEqual(`All tickets » #${rowPK} (test ticket 1)`);

        newTickets.push(rowPK);

        await createTicket("test ticket 2");

        // eslint-disable-next-line no-var
        var {rowPK, headerTitle} = await pkAndTitle();
        expect(headerTitle).toEqual(`All tickets » #${rowPK} (test ticket 2)`);

        newTickets.push(rowPK);

        await page.evaluate((sr, c) => {
            window.App.URLContext.history.pushPath({
                pathname: "/api/tickets/AllTickets",
                params: {
                    [c.URL_PARAM_SELECTED]: sr,
                    [c.URL_PARAM_DISPLAY_MODE]: c.DISPLAY_MODE_TABLE,
                },
            });
        }, newTickets, constants);
        await page.waitForNetworkIdle();

        // Quick filter is focused, so the key event "Delete" is consumed by it
        // unless we remove the focus
        await page.evaluate(() => {
            (document.activeElement as HTMLElement).blur();
        });

        await page.keyboard.press("Delete");
        await setTimeout(500);
        await page.locator("button>span ::-p-text(Yes)").click();
        await page.waitForNetworkIdle();

        const selected = await page.evaluate(() => {
            return window.App.URLContext.value.sr;
        });
        expect(selected).toEqual([]);
        const dialogs = await page.evaluate(() => {
            const dF = window.App.dialogFactory;
            return dF.state.children.size + dF.state.callbacks.size;
        });
        expect(dialogs).toEqual(0);
    });

    it("test insert window footer on dashboard", async () => {
        // await page.waitForSelector("div.dashboard-item>h2::-p-text(My Tickets)");
        // const mas = await page.$("div.dashboard-item>h2::-p-text(My Tickets)");
        await page.waitForSelector("div.dashboard-item>h2::-p-text(Tickets to work)");
        const mas = await page.$("div.dashboard-item>h2::-p-text(Tickets to work)");
        await mas.scrollIntoView();
        const insertButton = await mas.$("a.pi-plus-circle");
        await mas.dispose();
        await insertButton.click();
        await insertButton.dispose();
        await page.waitForSelector("div.l-bbar");
        const bbar = await page.$("div.l-bbar");
        const buttonCount = await (await bbar.getProperty("childElementCount")).jsonValue();
        expect(buttonCount).toEqual(1);

        const createButton = await bbar.$("button>span");
        await bbar.dispose();
        const text = await (await createButton.getProperty("textContent")).jsonValue();
        await createButton.dispose();
        expect(text).toEqual("Create");
    });

    it("delayed value component in grid, while changing 'row count' via QuickSearch",
    async () => {
        await page.evaluate(() => {
            window.App.URLContext.history.pushPath({
                pathname: "/api/groups/Groups"
            });
        });
        await page.waitForNetworkIdle();

        const qf = await page.$("input.l-grid-quickfilter");
        await qf.type("pr");
        await page.waitForNetworkIdle();

        const root = await page.$("div#root");
        const elemCount = await (await root.getProperty("childElementCount")).jsonValue();

        expect(elemCount).toBeGreaterThan(0);

        await qf.dispose();
        await root.dispose()
    });

    it("test choices view on an action window", async () => {
        await page.evaluate((c) => {
            window.App.URLContext.history.pushPath({
                pathname: "/api/tickets/AllTickets",
                params: {[c.URL_PARAM_DISPLAY_MODE]: c.DISPLAY_MODE_TABLE}
            });
        }, constants);
        await page.waitForNetworkIdle();

        await page.evaluate(() => {
            const ftid = window.App.URLContext.dataContext.mutableContext.pks[0];
            window.App.URLContext.history.replace({sr: [ftid]});
        });

        await page.locator('span ::-p-text(⚭)').click();
        await page.waitForNetworkIdle();
        await page.waitForSelector("label ::-p-text(into...)");
        await page.keyboard.type("gone");
        await page.waitForNetworkIdle();
        await page.waitForSelector(".p-autocomplete-items");
        const items = await page.$(".p-autocomplete-items");
        const itemCount = await (await items.getProperty("childElementCount")).jsonValue();
        expect(itemCount).toBeGreaterThan(0);

        await items.dispose();

        await page.evaluate(() => {
            (Object.values(window.App.URLContext.children)[0] as t.NavigationContext)
                .actionHandler.clearMod();
        });
        await page.locator(".p-dialog-header-close").click();
        await global.waitToMeet(page, () => {
            if (window.App.URLContext.children.length) return false;
            return true;
        });
    });

    it("test choices view on an insert action", async () => {
        await page.evaluate(() => {
            window.App.URLContext.history.pushPath({
                pathname: "/api/tickets/AllTickets"
            });
        });
        await page.waitForNetworkIdle();

        await page.keyboard.press("Insert");
        await page.waitForNetworkIdle();

        await page.waitForSelector("label ::-p-text(Summary)");

        await page.keyboard.type("test");

        await page.evaluate(() => {
            (Object.values(window.App.URLContext.children)[0] as t.NavigationContext)
                .dataContext.refStore.Leaves.order.focus();
        });
        await page.keyboard.type("a");

        await page.waitForSelector(".p-autocomplete-items");
        const items = await page.$(".p-autocomplete-items");
        const itemCount = await (await items.getProperty("childElementCount")).jsonValue();
        expect(itemCount).toBe(1);

        const item = await items.$("div");
        const subscription = await (await item.getProperty("textContent")).jsonValue();

        expect(subscription).toBe("SLA 3/2024 (aab)");

        await item.dispose();
        await items.dispose();

        await page.evaluate(() => {
            (Object.values(window.App.URLContext.children)[0] as t.NavigationContext)
                .actionHandler.clearMod();
        });
        await page.locator(".p-dialog-header-close").click();
        await global.waitToMeet(page, () => {
            if (window.App.URLContext.children.length) return false;
            return true;
        });
    });

    it("trading.InvoicesByJournal workflow button", async () => {
        await page.evaluate(() => {
             window.App.state.menu_data.filter(
                 md => md.label === 'Sales'
             )[0].items.filter(
                 md => md.label === 'Sales invoices (SLS)'
             )[0].command();
        });
        await page.waitForNetworkIdle();

        const invoice_id = await page.evaluate(() => {
            return window.App.URLContext.dataContext.mutableContext.rows[0][
                window.App.URLContext.static.actorData.pk_index
            ];
        });

        await page.evaluate((pk) => {
            window.App.URLContext.actionHandler.singleRow({}, pk);
        }, invoice_id);
        await page.waitForNetworkIdle();

        // await page.evaluate((pk) => {
        //     const { actionHandler } = window.App.URLContext;
        //     const action = actionHandler.findUniqueAction("wf2");
        //     actionHandler.runAction({actorId: "trading.InvoicesByJournal",
        //                              action_full_name: action.full_name, sr: pk});
        // }, invoice_id)
        // await page.waitForNetworkIdle();
        await page.locator("div>span>a::-p-text(Draft)").click();
        await page.waitForNetworkIdle();

        let wfState;
        wfState = await page.evaluate(() => {
            return window.App.URLContext.dataContext.mutableContext.data.workflow_buttons;
        });
        expect(wfState).toContain("<b>Draft</b>");

        // await page.evaluate((pk) => {
        //     const { actionHandler } = window.App.URLContext;
        //     const action = actionHandler.findUniqueAction("wf1");
        //     actionHandler.runAction({actorId: "trading.InvoicesByJournal",
        //                              action_full_name: action.full_name, sr: pk});
        // }, invoice_id);
        // await page.waitForNetworkIdle();
        await page.locator("div>span>a::-p-text(Registered)").click();
        await page.waitForNetworkIdle();

        wfState = await page.evaluate(() => {
            return window.App.URLContext.dataContext.mutableContext.data.workflow_buttons;
        });
        expect(wfState).toContain("<b>Registered</b>");
    });

    it("test grid_put", async () => {
        await page.evaluate((c) => {
            window.App.URLContext.history.pushPath({
                pathname: "/api/tickets/AllTickets",
                params: {[c.URL_PARAM_DISPLAY_MODE]: c.DISPLAY_MODE_TABLE}
            });
        }, constants);
        await page.waitForNetworkIdle();

        let firstSummary = await page.$(".l-grid-col-summary");
        await firstSummary.click();
        await firstSummary.waitForSelector('input');
        let input = await firstSummary.$('input');
        const oldSummary = await (await input.getProperty('value')).jsonValue();
        await input.dispose();

        const inputText = "Nothing important to say!";

        await firstSummary.click({clickCount: 3});
        await firstSummary.type(inputText);
        await page.keyboard.press("Enter");
        await page.waitForNetworkIdle();
        await firstSummary.dispose();
        await setTimeout(500);

        const ctxBackupSummary = await page.evaluate(() => {
            const sIndex = window.App.URLContext.static.actorData.col
                .filter(col => col.name === "summary")[0].fields_index;
            return window.App.URLContext.dataContext.contextBackup.rows[0][sIndex];
        });

        expect(ctxBackupSummary).toEqual(inputText);

        firstSummary = await page.$(".l-grid-col-summary");
        await firstSummary.click();
        await firstSummary.waitForSelector('input');

        input = await firstSummary.$("input");
        const newSummary = await (await input.getProperty('value')).jsonValue();
        await input.dispose();

        expect(newSummary).toBe(inputText);

        await firstSummary.click({clickCount: 3});
        await firstSummary.type(oldSummary);
        await page.keyboard.press("Enter");
        await page.waitForNetworkIdle();

        await firstSummary.dispose();
    });

    it("TicketsByParent ticket.description open in own window", async () => {
        await page.evaluate((c) => {
            window.App.URLContext.history.pushPath({
                pathname: "/api/tickets/AllTickets",
                params: {[c.URL_PARAM_LIMIT]: 100}
            })
        }, constants);
        await page.waitForNetworkIdle();


        const rows = await page.evaluate(() => {
            return window.App.URLContext.dataContext.mutableContext.rows;
        });

        for (let i = 0; i < rows.length; i++) {
            const row = rows[i];
            await page.evaluate((pk) => {
                window.App.URLContext.history.pushPath({
                    pathname: `/api/tickets/AllTickets/${pk}`,
                    params: {tab: 2}
                });
            }, row.id);
            await page.waitForNetworkIdle();

            const childRows = await page.evaluate(() => {
                return (Object.values(window.App.URLContext.children)[0] as t.NavigationContext)
                    .dataContext.mutableContext.rows;
            });
            if (childRows.length) {
                await page.evaluate((pk) => {
                    (Object.values(window.App.URLContext.children)[0] as t.NavigationContext)
                        .actionHandler.singleRow({}, pk, window.App.URLContext);
                }, childRows[0].id);
                await page.waitForNetworkIdle();
                break;
            }
        }

        await page.evaluate(() => {
            window.App.URLContext.history.replace({tab: 1});
        });

        await page.locator('span ::-p-text(⏏)').click();
        await page.waitForNetworkIdle();

        const success = await page.evaluate(() => {
            return window.App.URLContext.dataContext.mutableContext.success;
        })
        expect(success).toBe(true);

        const master_key = await page.evaluate((c) => {
            return window.App.URLContext.value[c.URL_PARAM_MASTER_PK];
        }, constants);
        expect(typeof master_key).toEqual("number");

        const master_type = await page.evaluate((c) => {
            return window.App.URLContext.value[c.URL_PARAM_MASTER_TYPE];
        }, constants);
        expect(typeof master_type).toEqual("number");

        const contextType = await page.evaluate(() => {
            return window.App.URLContext.contextType;
        });
        expect(contextType).toEqual(constants.CONTEXT_TYPE_TEXT_FIELD);
    });

    const typeToElement = async (text, label, input_dep) => {
        await page.waitForSelector(label);
        const elementLabel = await page.$(label);
        const elementParent = await elementLabel.getProperty("parentElement");
        const elementInput = await elementParent.$(input_dep);
        await elementInput.click();
        await elementInput.type(text);
        await elementLabel.dispose();
        await elementParent.dispose();
        await elementInput.dispose();
    };

    const createTicket = async (summary) => {
        await page.keyboard.press("Insert");
        await page.waitForNetworkIdle();

        await typeToElement(summary, "label ::-p-text(Summary)", ".l-card>input");

        await page.locator("button>span ::-p-text(Create)").click();
        await page.waitForNetworkIdle();
    };

    const pkAndTitle = async () => {
        const rowPK = await page.evaluate(() => {
            return window.App.URLContext.value.pk;
        });
        await page.waitForSelector(".l-detail-header>span");
        const detailHeader = await page.$(".l-detail-header>span");
        const headerTitle = await (await detailHeader.getProperty("textContent")).jsonValue();
        await detailHeader.dispose();
        return {rowPK, headerTitle}
    }

    it("Enter/Return key on a ChoiceList inside insert window must not submit the dialog", async () => {
        await page.evaluate(() => {
            window.App.URLContext.history.pushPath({
                pathname: "/api/contacts/Persons"
            })
        })
        await page.waitForNetworkIdle();

        await page.keyboard.press("Insert");
        await page.waitForNetworkIdle();

        await typeToElement("John", "label::-p-text(First name)", "input");
        await page.keyboard.press("Tab");
        await page.keyboard.type("Doe");
        await page.keyboard.press("Tab");
        await page.keyboard.press("ArrowDown");
        await page.keyboard.press("ArrowDown");
        await page.keyboard.press("Enter");

        const childCount = await page.evaluate(() => {
            return Object.values(window.App.URLContext.children).length;
        });

        expect(childCount).toBe(1);

        const actionFullName = await page.evaluate(() => {
            const insertCtx = Object.values(window.App.URLContext.children)[0];
            return (insertCtx as t.NavigationContext).value.action_full_name;
        });

        expect(actionFullName.endsWith(".insert")).toBe(true);

        await page.evaluate(() => {
            (Object.values(window.App.URLContext.children)[0] as t.NavigationContext).actionHandler.clearMod();
        });
    });


    it("Eject button on CommentsByRFC body", async () => {
        await page.evaluate(() => {
            window.App.URLContext.history.pushPath({
                pathname: "/api/tickets/AllTickets/1"
            });
        });
        await page.waitForNetworkIdle();

        const getSlaveHtml = async () => {
            return await page.evaluate(() => {
                return window.App.URLContext.dataContext.refStore
                    .slaveLeaves["comments.CommentsByRFC"].state.value;
            });
        }

        let html = await getSlaveHtml();
        if (html === '<div class="htmlText"></div>') {
            await page.locator("button>span.pi-angle-double-left").click();
            await page.waitForNetworkIdle();

            html = await getSlaveHtml();
        }

        while (html === '<div class="htmlText"></div>') {
            await page.locator("button>span.pi-angle-right").click();
            await page.waitForNetworkIdle();

            html = await getSlaveHtml();
        }

        await page.waitForSelector("div.p-panel-header>span::-p-text(Comments)");
        const headerTitle = await page.$("div.p-panel-header>span::-p-text(Comments)");
        const header = await headerTitle.getProperty("parentElement");
        await headerTitle.dispose();
        const eject = await header.$("::-p-text(⏏)");
        await header.dispose();
        await eject.click();
        await eject.dispose();
        await page.waitForNetworkIdle();

        const url = await page.evaluate(() => window.location.href);
        expect(url).toContain("/api/comments/CommentsByRFC");
    });

    it.only("insert (twice), merge, and delete", async () => {
        await page.evaluate(() => {
            window.App.URLContext.history.pushPath({
                pathname: "/api/tickets/AllTickets"
            });
        });
        await page.waitForNetworkIdle();

        const initRowCount = await page.evaluate(() => {
            return window.App.URLContext.dataContext.mutableContext.count;
        });

        const t1 = "test ticket 1";

        await createTicket(t1);

        // eslint-disable-next-line no-var
        var {rowPK, headerTitle} = await pkAndTitle();
        expect(headerTitle).toEqual(`All tickets » #${rowPK} (test ticket 1)`);

        await createTicket("test ticket 2");

        // eslint-disable-next-line no-var
        var {rowPK, headerTitle} = await pkAndTitle();
        expect(headerTitle).toEqual(`All tickets » #${rowPK} (test ticket 2)`);

        await page.reload();
        await page.waitForNetworkIdle();

        await page.locator("button>span ::-p-text(⚭)").click();
        await page.waitForNetworkIdle();
        await typeToElement(t1, "label ::-p-text(into...)", ".l-card>span>input");
        await page.waitForNetworkIdle();
        await page.waitForSelector(".p-autocomplete-items");
        const items = await page.$(".p-autocomplete-items");
        const item = await items.$("div");
        await item.click();

        await items.dispose();
        await item.dispose();

        await page.locator("button>span ::-p-text(OK)").click();
        await page.locator("button>span ::-p-text(Yes)").click();
        await page.waitForNetworkIdle();

        // eslint-disable-next-line no-var
        var {rowPK, headerTitle} = await pkAndTitle();
        expect(headerTitle).toEqual(`All tickets » #${rowPK} (test ticket 1)`);

        await page.reload();
        await page.waitForNetworkIdle();

        await page.locator("button.l-button-delete_selected").click();
        await page.locator("button>span ::-p-text(Yes)").click();
        await page.waitForNetworkIdle();

        // eslint-disable-next-line no-var
        var {rowPK, headerTitle} = await pkAndTitle();
        expect(headerTitle).toEqual("All tickets");

        const endRowCount = await page.evaluate(() => {
            return window.App.URLContext.dataContext.mutableContext.count;
        });

        expect(initRowCount).toEqual(endRowCount);
    });
});
