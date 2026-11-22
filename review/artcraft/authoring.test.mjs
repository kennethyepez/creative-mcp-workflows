import assert from 'node:assert/strict';
import test from 'node:test';
import { appIds, describeOperations, encodeOperations } from './authoring.mjs';

function encode(app, steps) {
    return encodeOperations(app, JSON.stringify(steps));
}

test('the catalog contains 53 advertised operations across 17 apps', () => {
    assert.equal(appIds.length, 17);
    const count = appIds.reduce((total, app) => total + describeOperations(app).length, 0);
    assert.equal(count, 53);
});

test('a revision retains the order and arguments of two WordCraft edits', () => {
    const steps = [
        { name: 'append_text', args: { text: 'Studio draft' } },
        { name: 'replace_text', args: { find: 'draft', text: 'final' } },
    ];
    const { value } = encode('wordcraft', steps);
    assert.equal(value[0], '\u001e');
    assert.deepEqual(JSON.parse(value.slice(1)), steps);
});

test('PdfCraft accepts the documented clockwise page rotation', () => {
    const { value } = encode('pdfcraft', [
        { name: 'rotate_page', args: { page: 1, degrees: '90' } },
    ]);
    assert.ok(value);
});

test('malformed and oversized step lists are rejected', () => {
    assert.ok(encodeOperations('wordcraft', '[').error);
    assert.ok(encodeOperations('wordcraft', ' '.repeat(8193)).error);
    assert.ok(encode('wordcraft', []).error);
    const step = { name: 'append_text', args: { text: 'Sample' } };
    assert.ok(encode('wordcraft', Array(5).fill(step)).error);
});

test('other apps’ operations and unrecognized argument fields are rejected', () => {
    assert.ok(encode('unknown', [
        { name: 'append_text', args: { text: 'Sample' } },
    ]).error);
    assert.ok(encode('wordcraft', [
        { name: 'rotate_page', args: { page: 1, degrees: '90' } },
    ]).error);
    assert.ok(encode('pdfcraft', [
        { name: 'rotate_page', args: { page: 1, degrees: '90', label: 'extra' } },
    ]).error);
    assert.ok(encode('pdfcraft', [
        { name: 'rotate_page', args: { page: 1, degrees: '45' } },
    ]).error);
});

test('GridCraft accepts text and rejects formula-like input', () => {
    const cell = text => [{ name: 'set_cell', args: { cell: 'A1', text } }];
    assert.ok(encode('gridcraft', cell('Studio budget')).value);
    assert.match(encode('gridcraft', cell('=1+1')).error, /plain text/);
});
