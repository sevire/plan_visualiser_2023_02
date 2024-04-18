export interface Colour {
    red: number,
    green: number,
    blue: number,
    alpha: number
}

export interface Point {
    top: number,
    left: number
}


/*
* A lot of shapes can be defined by specifying the properties of a notianal box that they sit within.
* A rectangle, a rounded rectangle (with default corner radius), a diamond, an isoceles triangle etc.
*
* In some cases additional information may vary the shape (corner radius).
*
* In other cases a rectangle isn't good enough - e.g a star.  In those cases to define a shape we will
* need the coordinates of all the points and plot them each individually.
*
* The ShapePlotData interface will encapsulate these various ways of representing and plotting a shape.
* */
export interface    BoxShapeDimensions {
    top: number,
    left: number,
    width: number,
    height: number,
}

// For a generic shape (i.e. not one based on a rectangle) this allows an arbitrary number of points
// to be represented.
export interface ShapePoints extends Array<Point> { }
export type ShapeDimensionData = BoxShapeDimensions
export type ShapeName = "RECTANGLE" | "DIAMOND"

export type ShapePlotData = ShapeDimensionData

export interface ShapeData {
    shape_details: {
        "shape_name": string,
        "shape_plot_dims": ShapePlotData,
    }
}

export interface ShapesData extends Array<ShapeData> {}
