from math import radians, cos, sin

def mult_vector_by_matrix(mat, v):
    x = (mat[0] * v[0]) + (mat[4] * v[1]) +	(mat[8] * v[2]) + mat[12]
    y = (mat[1] * v[0]) + (mat[5] * v[1]) +	(mat[9] * v[2]) + mat[13]
    z = (mat[2] * v[0]) + (mat[6] * v[1]) +	(mat[10] * v[2]) + mat[14]
    return x,y,z
    
def polar_vector(angle, length):
    angle = radians(angle)
    return ((length * cos(angle), length * sin(angle), 0.0))

def spherical_vector(r,a,p):
    a = radians(a)
    p = radians(p)
    return ([r*cos(a)*sin(p), r*sin(a)*sin(p), r * cos(p)], Numeric.Float)
