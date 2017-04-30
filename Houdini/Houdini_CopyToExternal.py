selnode = hou.selectedNodes()
for node in hou.selectedNodes():
    selPath = node.path()
sel = selPath.split("/")[-2]

#scale = 1  #somehow, normal meshes, that werent transfered need to have their z axis inverted otherwise they show flipped
#for node in hou.node('obj/'+sel).children():
#    if "ImportScript" in node.name(): scale = 1
#    else: scale = -1

hou.node('obj/'+sel).createNode("python", "ExportScript" )
hou.node('obj/'+sel+'/ExportScript/').setParms({"python": '''
# encoding: utf-8
import tempfile, os, random, sys, re

filePath = tempfile.gettempdir() + os.sep + ".." + os.sep + "ODVertexData.txt"

node = hou.pwd()
geo = node.geometry()

if len(geo.points()) > 0:
    f = open(filePath, "w")

    f.write("VERTICES:"+str(len(geo.points())) + "\\n")
    for point in geo.points():
        pos = point.position()
        f.write(str(pos[0]) + " " + str(pos[1]) + " " + str(pos[2]) + "\\n")

    uvs = []
    check = geo.findVertexAttrib("uv")
    f.write("POLYGONS:"+str(len(geo.prims())) + "\\n")
    count = 0
    for (fid, prim) in enumerate(geo.prims()):
        ppoint = ""
        for point in reversed(prim.vertices()):
             ppoint += "," + str(hou.Vertex.point(point).number())
             if check != None:
                uvs.append(str(point.attribValue("uv")[0]) + " " + str(point.attribValue("uv")[1]) + ":PLY:" + str(count) + ":PNT:" + str(hou.Vertex.point(point).number()) + "\\n")
        surf = "Default"
        polytype = "FACE"

        transform = ppoint[1:].split(",")
        transform.insert(0, transform[-1])
        transform = transform[:-1]
        ppoint = ",".join(transform)

        f.write(ppoint + ";;" + surf + ";;" + polytype + "\\n")
        count += 1

    attribs = geo.pointAttribs()
    weights = []
    for attrib in attribs:
        if attrib.type() == hou.attribType.Point:
            if attrib.dataType() == hou.attribData.Float and attrib.size() == 1:
                weights.append(attrib.name())

    if len(weights) > 0:
        for wmap in weights:
            wmapName = re.sub(r"_..", lambda m: chr(int(m.group()[1:], 16)), wmap.lower())
            attrib = wmap
            f.write("WEIGHT:" + wmapName + "\\n")
            for p in geo.points():
                f.write(str(p.attribValue(wmap))+ "\\n")

    if len(uvs) > 0:
        f.write("UV:UVMap:"+ str(len(uvs)) + "\\n")
        for uv in uvs:
            f.write(uv)
    f.close()
    '''})

hou.node('obj/'+sel).createNode("convert", "ODConvertToPolygon" )
hou.node('obj/'+sel+'/ODConvertToPolygon/').setInput(0, hou.node(selPath))
hou.node('obj/'+sel+'/ExportScript/').setInput(0, hou.node('obj/'+sel+'/ODConvertToPolygon/'))


#hou.node('obj/'+sel+'/ExportScript/').setInput(0, hou.node(selPath))
hou.node('obj/'+sel+'/ExportScript/').setDisplayFlag(True)
hou.node('obj/'+sel+'/ExportScript/').setRenderFlag(True)
hou.node('obj/'+sel+'/ExportScript/').setCurrent(1, False)
hou.node('obj/'+sel+'/ExportScript/').cook(force=True, frame_range=(int(hou.frame()),int(hou.frame())))
hou.node('obj/'+sel+'/ExportScript/').destroy()
hou.node('obj/'+sel+'/ODConvertToPolygon/').destroy()
