"""
Created on Fri Jan 11 16:37:47 2019

@author: lpaone
"""
import copy
import unittest

from pycivil.EXAGeometry.geometry import (
    Edge2d,
    Edge3d,
    Node2d,
    Node3d,
    Point2d,
    Point3d,
    Polyline2d,
    Polyline3d,
    Seg2d,
    Vector2d,
    Vector3d,
    affineSum2d,
    areaFromTria3D,
    twoPointsDivide,
    twoPointsOffset,
)
from pycivil.EXAGeometry.shapes import Frame, ShapeCircle, ShapePoly


class Test(unittest.TestCase):
    def test_00_Points2d_Coordinates(self):

        # try:
        #     import EXADisplay as vis
        # except:
        #     print("EXADisplay error !!!")

        p1 = Point2d(0, 0)
        p2 = Point2d(1, 2.0 / 3)
        p3 = Point2d(1, 2)

        self.assertEqual(p1.x, 0)
        self.assertEqual(p1.y, 0)

        self.assertEqual(p2.x, 1)
        self.assertEqual(p2.y, 2.0 / 3)

        self.assertEqual(p1.x, 0)
        self.assertEqual(p1.y, 0)

        self.assertEqual(p3.x, 1)
        self.assertEqual(p3.y, 2)

        p1 = Point2d(coords=(0, 0))
        p2 = Point2d(coords=(1, 2.0 / 3))
        p3 = Point2d(coords=(1, 2))

        self.assertEqual(p1.x, 0)
        self.assertEqual(p1.y, 0)

        self.assertEqual(p2.x, 1)
        self.assertEqual(p2.y, 2.0 / 3)

        self.assertEqual(p1.x, 0)
        self.assertEqual(p1.y, 0)

        self.assertEqual(p3.x, 1)
        self.assertEqual(p3.y, 2)

        # Polyline3D testing start
        nodesLst = [
            Node3d(1, 0.0, 0.0, 0),
            Node3d(2, 300.0, 0.0, 0),
            Node3d(3, 300.0, 500.0, 0),
            Node3d(4, 0.0, 500.0, 0),
        ]
        poly3 = Polyline3d(nodesLst)

        poly3.setClosed()
        self.assertTrue(poly3.isClosed())

        # Op for Point3d
        p1 = Point3d(0.0, 0.0, 1.0)
        p2 = Point3d(1.0, 1.0, 0.0)
        p3 = p1 + p2

        # print("p1+p2 is: %s\n" % p3)

        # Op for Node3d
        n1 = Node3d(0.0, 0.0, 1.0)
        n2 = Node3d(1.0, 1.0, 0.0)
        # print(n1)
        # print(n2)
        # print("n1+n2 is: %s\n" % n3)

        # Op for Vector3d
        v1 = Vector3d(0.0, 0.0, 1.0)
        v2 = Vector3d(1.0, 1.0, 0.0)
        # print(v1)
        # print(v2)
        # print("v1+v2 is: %s\n" % v3)

        # Cross vector for Vector3d
        v1 = Vector3d(1.0, 0.0, 0.0)
        v2 = Vector3d(0.0, 1.0, 0.0)
        # print(v1)
        # print(v2)
        v1.cross(v2)
        # print("v1.cross(v2) is: %s\n" % v3)

        # Norm of vector for Vector3d
        v1 = Vector3d(5.0, 0.0, 0.0)
        # print(v1)
        # print("v1.norm() is: %d\n" % v1.norm())

        # Normalizition of vector for Vector3d
        v1.normalize()
        # print("v1.normalize() is: %s" % v1)

        # Vector 3d from two points
        p1 = Point3d(1.0, 0.0, 0.0)
        p2 = Point3d(2.0, 0.0, 0.0)
        # print(p1)
        # print(p2)
        v1 = Vector3d(p1, p2)
        # print("v1 from two points: %s\n" % v1)

        # Generic Shape Abstraact
        # sec = Shape()
        # print(sec)

        # Frame with Shape
        nodesLst = [
            Node2d(0.0, 0.0, 1),
            Node2d(300.0, 0.0, 2),
            Node2d(300.0, 500.0, 3),
            Node2d(0.0, 500.0, 4),
        ]
        poly = Polyline2d(nodesLst)
        shape = ShapePoly(poly)

        edge1 = Edge3d(Node3d(1, 1, 1, 1), Node3d(2, 3, 3, 3))
        frame1 = Frame(edge1)

        frame1.setShape(shape)
        # print(frame1)

        # Build a normal frame
        # print("We want build a typical frame 3D")

        n1 = Node3d(1.0, 1.0, 1.0, 1)
        n2 = Node3d(6.0, 6.0, 6.0, 2)

        axis = Edge3d(n1, n2)

        frame_typical = Frame(axis)

        frame_typical.setReference(Point3d(1.0, 1.0, 0.0))
        frame_typical.setReference(1.0, 1.0, 0.0)
        # print(frame_typical)

        # print(frame_typical.getXLocalAxis())
        # print(frame_typical.getYLocalAxis())
        # print(frame_typical.getZLocalAxis())

        # Polygonar
        secPoly = ShapePoly(0.0, 0.0, 1, 300.0, 0.0, 2, 300.0, 500.0, 3, 0.0, 500.0, 4)

        frame_typical.setShape(secPoly)

        # print(frame_typical)

        secPoly.translate(Point2d(150.0, 250.0), Point2d(0.0, 0.0))

        # print(frame_typical)

        axis = Edge3d(1.0, 1.0, 1.0, 1, 6.0, 6.0, 6.0, 2)

        # print(axis)

        frame_typical = Frame(100.0, 100.0, 100.0, 1, 600.0, 600.0, 600.0, 2)
        frame_typical.setReference(100.0, 100.0, 0.0)
        frame_typical.setShape(secPoly)

        frame_typical2 = Frame(15.0, 25.0, 35.0, 1, 60.0, 70.0, 90.0, 2)
        frame_typical2.setReference(15.0, 25.0, 10.0)
        frame_typical2.setShape(secPoly)

        # print(frame_typical)

        # Op for Vector2d
        v1 = Vector2d(vx=0.0, vy=0.0)
        v2 = Vector2d(vx=1.0, vy=1.0)
        # print(v1)
        # print(v2)
        # print("v1+v2 is: %s\n" % v3)

        # Cross vector for Vector2d
        v1 = Vector2d(vx=1.0, vy=0.0)
        v2 = Vector2d(vx=0.0, vy=1.0)
        # print(v1)
        # print(v2)
        v1.cross(v2)
        # print("v1.cross(v2) is: %s\n" % v3)

        # Norm of vector for Vector2d
        v1 = Vector2d(vx=5.0, vy=0.0)
        # print(v1)
        # print("v1.norm() is: %d\n" % v1.norm())

        # Normalizition of vector for Vector2d
        v1.normalize()
        # print("v1.normalize() is: %s" % v1)

        # Vector 2d from two points
        p1 = Point2d(1.0, 0.0)
        p2 = Point2d(2.0, 0.0)
        # print(p1)
        # print(p2)
        v1 = Vector2d(p1, p2)
        # print("v1 from two points: %s\n" % v1)

        # Seg2d from two points
        Seg2d(p1, p2)
        # print("Distance betwen p1 and p2 is %1.6f" % p1.distance(p2))
        # print(seg)

        self.assertRaises(ValueError, Point2d, None, None)
        # if pnull.isNull():
        #     print("Point Null Point2d(None,None) is Null !!!")

        # if not p1.isNull():
        #     print("Point p1 Point2d(1.0,0.0) is not Null !!!")

        # visualizer = vis.Visualizer()
        # visualizer.addStruComponent(frame_typical)
        # visualizer.addStruComponent(secPoly)
        # visualizer.display()

        # vis.test_extrusion()
        # vis.test_sec()
        # vis.test_vector_sec()
        # vis.test_axis()
        # vis.test_transform()

    def test_01_Points2d_scalarVector(self):
        p1 = Point2d(1, 2)
        p2 = 2 * p1
        self.assertEqual(p2.x, 2, "x coordinate")
        self.assertEqual(p2.y, 4, "y coordinate")

        p3 = p2 * 2
        self.assertEqual(p3.x, 4, "x coordinate")
        self.assertEqual(p3.y, 8, "y coordinate")

    def test_02_Node2d_properties(self):

        # instance
        node = Node2d(101, 2.3, 4)

        self.assertEqual(node.x, 101)
        self.assertEqual(node.y, 2.3)
        self.assertEqual(node.idn, 4)

        # modified
        node.x = 1
        node.y = 2
        node.idn = 1

        self.assertEqual(node.x, 1)
        self.assertEqual(node.y, 2)
        self.assertEqual(node.idn, 1)

        # default args
        node = Node2d()
        self.assertEqual(node.x, 0.0)
        self.assertEqual(node.y, 0.0)
        self.assertEqual(node.idn, -1)

    def test_03_Polyline2d_properties(self):
        n1 = Node2d(0.0, 0.0, 1)
        n2 = Node2d(300.0, 0.0, 2)
        n3 = Node2d(300.0, 500.0, 3)
        n4 = Node2d(0.0, 500.0, 4)

        # Bad formed
        with self.assertRaises(TypeError):
            Polyline2d([n1, n2], 2, 3)

        # Well formed
        Polyline2d([n1, n2, n3, n4])

    def test_04_Polyline2d_methods(self):

        # Polyline2D testing start
        nodesLst = [
            Node2d(0.0, 0.0, 1),
            Node2d(300.0, 0.0, 2),
            Node2d(300.0, 500.0, 3),
            Node2d(0.0, 500.0, 4),
        ]
        poly2 = Polyline2d(nodesLst)

        self.assertEqual(poly2.size(), 4)
        self.assertFalse(poly2.isClosed())

        poly2.setClosed()
        self.assertEqual(poly2.size(), 5)
        self.assertTrue(poly2.isClosed())

    def test_05_Edge2d_properties(self):
        n1 = Node2d(0.0, 0.0, 1)
        n2 = Node2d(300.0, 0.0, 2)

        with self.assertRaises(TypeError):
            Edge2d(n1)

        with self.assertRaises(TypeError):
            Edge2d(n1, 1)

        edge1 = Edge2d(n1, n2)

        ni = edge1.nodeI()
        nj = edge1.nodeJ()

        self.assertEqual(ni.x, 0.0)
        self.assertEqual(ni.y, 0.0)
        self.assertEqual(ni.idn, 1)

        self.assertEqual(nj.x, 300.0)
        self.assertEqual(nj.y, 0.0)
        self.assertEqual(nj.idn, 2)

    def test_06_Node3d_properties(self):

        # instance
        node = Node3d(1, 2, 3, 4)

        self.assertEqual(node.x, 1)
        self.assertEqual(node.y, 2)
        self.assertEqual(node.z, 3)
        self.assertEqual(node.idn, 4)

        # defalut args
        node = Node3d()

        self.assertEqual(node.x, 0.0)
        self.assertEqual(node.y, 0.0)
        self.assertEqual(node.z, 0.0)
        self.assertEqual(node.idn, -1)

    def test_07_Edge3d_properties(self):
        edge1 = Edge3d(Node3d(1, 1, 1, 1), Node3d(2, 3, 3, 3))
        edge2 = Edge3d(Node3d(1, 3, 3, 3), Node3d(2, 3, 3, 0))

        self.assertEqual(edge1.nodeI().x, 1)
        self.assertEqual(edge1.nodeI().y, 1)
        self.assertEqual(edge1.nodeI().z, 1)
        self.assertEqual(edge1.nodeI().idn, 1)

        self.assertEqual(edge1.nodeJ().x, 2)
        self.assertEqual(edge1.nodeJ().y, 3)
        self.assertEqual(edge1.nodeJ().z, 3)
        self.assertEqual(edge1.nodeJ().idn, 3)

        self.assertEqual(edge2.nodeI().x, 1)
        self.assertEqual(edge2.nodeI().y, 3)
        self.assertEqual(edge2.nodeI().z, 3)
        self.assertEqual(edge2.nodeI().idn, 3)

        self.assertEqual(edge2.nodeJ().x, 2)
        self.assertEqual(edge2.nodeJ().y, 3)
        self.assertEqual(edge2.nodeJ().z, 3)
        self.assertEqual(edge2.nodeJ().idn, 0)

    def test_08_Vector2d_properties(self):

        # instance 2 float args
        v = Vector2d(vx=1.0, vy=2.0)
        self.assertEqual(v.vx, 1.0)
        self.assertEqual(v.vy, 2.0)

        # instance 2 int args
        v = Vector2d(vx=1, vy=2)
        self.assertEqual(v.vx, 1)
        self.assertEqual(v.vy, 2)

        # instance 2 int and float args
        v = Vector2d(vx=1, vy=2.0)
        self.assertEqual(v.vx, 1)
        self.assertEqual(v.vy, 2)

        # instance 2 args
        p1 = Point2d(1, 1)
        p2 = Point2d(2, 3)
        v = Vector2d(p1, p2)
        self.assertEqual(v.vx, 1)
        self.assertEqual(v.vy, 2)

        # default args
        v = Vector2d()
        self.assertEqual(v.vx, 0.0)
        self.assertEqual(v.vy, 0.0)

        with self.assertRaises(TypeError, msg="not sended"):
            Vector2d(1, 2, 3)

        with self.assertRaises(TypeError, msg="not sended"):
            Vector2d(1)

        with self.assertRaises(TypeError, msg="not sended"):
            Vector2d(1, Point2d())

    def test_09_Vector3d_properties(self):

        # instance 3 float args
        v = Vector3d(1.0, 2.0, 3.0)
        self.assertEqual(v.vx, 1.0)
        self.assertEqual(v.vy, 2.0)
        self.assertEqual(v.vz, 3.0)

        # instance 3 int args
        v = Vector3d(1, 2, 3)
        self.assertEqual(v.vx, 1)
        self.assertEqual(v.vy, 2)
        self.assertEqual(v.vz, 3)

        # instance 2 args
        p1 = Point3d(1, 1, 1)
        p2 = Point3d(2, 3, 4)
        v = Vector3d(p1, p2)
        self.assertEqual(v.vx, 1)
        self.assertEqual(v.vy, 2)
        self.assertEqual(v.vz, 3)

        # default args
        v = Vector3d()
        self.assertEqual(v.vx, 0.0)
        self.assertEqual(v.vy, 0.0)
        self.assertEqual(v.vz, 0.0)

    def test_10_Frame_properties(self):
        edge1 = Edge3d(Node3d(1, 1, 1, 1), Node3d(2, 3, 3, 3))
        edge2 = Edge3d(Node3d(1, 3, 3, 3), Node3d(2, 3, 3, 0))

        Frame(edge1)
        Frame(edge2)

        with self.assertRaises(TypeError, msg="not sended"):
            Frame(1)

        with self.assertRaises(TypeError, msg="not sended"):
            Frame(1, 1)

    def test_11_ShapePoly_properties(self):

        nodesLst = [
            Node2d(0.0, 0.0, 1),
            Node2d(300.0, 0.0, 2),
            Node2d(300.0, 500.0, 3),
            Node2d(0.0, 500.0, 4),
        ]
        poly = Polyline2d(nodesLst)

        ShapePoly(poly)

    def test_12_MidPoint_2D(self):
        v0 = Point2d(0.0, 0.0)
        v1 = Point2d(1.0, 0.0)
        self.assertEqual(v0.midpoint(v1).x, 0.5)
        self.assertEqual(v0.midpoint(v1).y, 0.0)

    def test_13_AreaFromTria_2D(self):
        v0 = Point2d(0.0, 0.0)
        v1 = Point2d(1.0, 0.0)
        v2 = Point2d(0.5, 1.0)
        self.assertEqual(
            Point2d.areaFromTria(v0, v1, v2),
            v0.distance(v1) * v0.midpoint(v1).distance(v2) / 2,
        )

    def test_14_AreaFromTria_3D(self):
        v0 = Point2d(0.0, 0.0)
        v1 = Point2d(1.0, 0.0)
        v2 = Point2d(0.5, 1.0)
        area2D = Point2d.areaFromTria(v0, v1, v2)

        p0 = Point3d(0.0, 0.0, 2.0)
        p1 = Point3d(1.0, 0.0, 2.0)
        p2 = Point3d(0.5, 1.0, 2.0)
        area3D_1 = areaFromTria3D(p0, p1, p2)

        self.assertEqual(area2D, area3D_1)

        p0 = Point3d(0.0, 2.0, 0.0)
        p1 = Point3d(1.0, 2.0, 0.0)
        p2 = Point3d(0.5, 2.0, 1.0)
        area3D_2 = areaFromTria3D(p0, p1, p2)

        self.assertEqual(area2D, area3D_2)

    def test_15_shape_circle(self):

        # First constructor
        shape1 = ShapeCircle(20, 100, 200)
        self.assertEqual(shape1.getRadius(), 20)
        self.assertEqual(shape1.getShapePoint("O").x, 100)
        self.assertEqual(shape1.getShapePoint("O").y, 200)

        # Second constructor
        shape2 = ShapeCircle(20, center=Point2d(101, 201))
        self.assertEqual(shape2.getRadius(), 20)
        self.assertEqual(shape2.getShapePoint("O").x, 101)
        self.assertEqual(shape2.getShapePoint("O").y, 201)

    def test_16_vector_rotate(self):
        v1 = Vector2d(Point2d(0, 0), Point2d(5, 5))
        v2 = copy.deepcopy(v1).rotate(90)
        self.assertAlmostEqual(v2.vx, -5)
        self.assertAlmostEqual(v2.vy, +5)

        self.assertAlmostEqual(v1.normalize().cross(v2.normalize()), 1)

    def test_17_sum_affine(self):
        p = Point2d(1, 1)
        v = Vector2d(vx=2, vy=3)
        psum = affineSum2d(p, v)
        self.assertEqual(psum.x, 3)
        self.assertEqual(psum.y, 4)

    def test_18_points_divide(self):
        p0 = Point2d(1, 1)
        p1 = Point2d(2, 2)
        self.assertRaises(ValueError, twoPointsDivide, p0, p1, 0)

        arr1 = twoPointsDivide(p0, p1, 1)
        self.assertTrue(len(arr1) == 2)
        self.assertTrue(arr1[0] == p0)
        self.assertTrue(arr1[1] == p1)

        arr2 = twoPointsDivide(p0, p1, 4)
        self.assertTrue(len(arr2) == 5)
        self.assertTrue(arr2[0] == p0)
        self.assertTrue(arr2[1] == Point2d(1.25, 1.25))
        self.assertTrue(arr2[2] == Point2d(1.50, 1.50))
        self.assertTrue(arr2[3] == Point2d(1.75, 1.75))
        self.assertTrue(arr2[4] == p1)

    def test_19_points_offset(self):
        p0 = Point2d(1, 1)
        p1 = Point2d(1, 2)
        pp0, pp1 = twoPointsOffset(p0, p1, 10)
        self.assertAlmostEqual(pp0.x, Point2d(-9, 1).x)
        self.assertAlmostEqual(pp0.y, Point2d(-9, 1).y)
        self.assertAlmostEqual(pp1.x, Point2d(-9, 2).x)
        self.assertAlmostEqual(pp1.y, Point2d(-9, 2).y)


if __name__ == "__main__":
    unittest.main()
