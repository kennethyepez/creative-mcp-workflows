import { z } from 'zod';
import { encodeOperations } from './authoring.mjs';

export const vectorSvgTool = {
    description: 'Create an editable SVG in VectorCraft. Draw one filled rectangle or ellipse on a 640 by 400 canvas. Coordinates are in canvas units and color is #RRGGBB. Use get_artcraft_file_job with the returned ID to download the SVG.',
    inputSchema: {
        shape: z.enum(['rectangle', 'ellipse']),
        x: z.number().min(0).max(639), y: z.number().min(0).max(399),
        width: z.number().min(1).max(640), height: z.number().min(1).max(400),
        color: z.string().regex(/^#[a-fA-F0-9]{6}$/),
    },
    annotations: { readOnlyHint: false, destructiveHint: true, idempotentHint: false, openWorldHint: false },
};

// The production handler runs this contract after checking the owner's OAuth grant.
export function encodeVectorSvg(args) {
    const parsed = z.strictObject(vectorSvgTool.inputSchema).safeParse(args);
    if (!parsed.success) return { error: 'Enter a supported shape and valid canvas values.' };
    const shape = parsed.data;
    if (shape.x + shape.width > 640 || shape.y + shape.height > 400) {
        return { error: 'Keep the shape within the 640 by 400 canvas.' };
    }
    return encodeOperations('vectorcraft', JSON.stringify([{ name: 'draw_shape', args: shape }]));
}
