import { z } from 'zod';
import catalog from './authoring-actions.json' with { type: 'json' };

const types = Object.fromEntries(Object.entries(catalog.types).map(([key, spec]) => {
    if (spec.type === 'number') return [key, z.number().min(spec.min).max(spec.max)];
    if (spec.type === 'enum') return [key, z.enum(spec.values)];
    if (spec.type === 'table') {
        const cell = z.string().max(spec.cell_max).refine(text => !/[\u0000-\u001f]/.test(text));
        const table = z.array(z.array(cell).min(1).max(spec.max)).min(1).max(spec.max);
        return [key, table.refine(rows => rows.every(row => row.length === rows[0].length))];
    }
    const text = z.string().min(1).max(spec.max);
    return [key, (spec.pattern ? text.regex(new RegExp(spec.pattern)) : text)
        .refine(value => value.trim() && !/[\u0000-\u0009\u000b-\u001f]/.test(value))];
}));

export const appOperations = catalog.apps;
export const appIds = Object.keys(appOperations);
export const stepName = z.string().regex(/^[a-z][a-z_]{2,39}$/);
const parameter = z.union([z.string().max(360), z.number(), z.array(z.array(z.string().max(80)).max(8)).max(8)]);
const requestedSteps = z.array(z.object({ name: stepName, args: z.record(z.string(), parameter).optional() }).strict()).min(1).max(4);

const schemas = Object.fromEntries(Object.entries(appOperations).map(([app, steps]) => [app,
    Object.fromEntries(Object.entries(steps).map(([name, operation]) => [name,
        z.object(Object.fromEntries(Object.entries(operation.fields).map(([key, type]) => [key, types[type]]))).strict()])),
]));

export function describeOperations(app) {
    return Object.entries(appOperations[app]).map(([name, operation]) => ({ name, description: operation.summary,
        arguments: Object.fromEntries(Object.entries(operation.fields).map(([key, type]) => [key, catalog.types[type]])),
    }));
}

export function encodeOperations(app, operationsJson) {
    if (!Object.hasOwn(schemas, app)) return { error: 'Unknown ArtCraft app.' };
    if (typeof operationsJson !== 'string' || operationsJson.length > 8192) {
        return { error: 'Provide operations_json as a JSON string of up to 8,192 characters.' };
    }
    let requested;
    try {
        requested = requestedSteps.safeParse(JSON.parse(operationsJson));
    } catch {
        return { error: 'operations_json must contain a JSON array of steps.' };
    }
    if (!requested.success) return { error: 'Provide up to four steps as {name, args} objects.' };
    const validated = [];
    for (const { name, args } of requested.data) {
        const spec = Object.hasOwn(schemas[app], name) && schemas[app][name];
        const check = spec && spec.safeParse(args ?? {});
        if (!check?.success) return { error: `Invalid arguments for ${name}. Use list_artcraft_tools for its accepted fields.` };
        if (app === 'gridcraft' && [check.data.text, ...(check.data.rows?.flat() ?? [])]
            .some(value => typeof value === 'string' && /^[=+\-@]/.test(value.trimStart()))) {
            return { error: 'Spreadsheet cells in this tool accept plain text.' };
        }
        validated.push({ name, args: check.data });
    }
    // Legacy revision entries reject control characters. This type marker keeps both formats replayable.
    const value = '\u001e' + JSON.stringify(validated);
    const workerLength = JSON.stringify(value).replace(/[^\x00-\x7f]/g, '\\u0000').length;
    if (workerLength > 6400 || new TextEncoder().encode(value).length > 3600) return { error: 'These operations exceed the request size.' };
    return { value };
}
