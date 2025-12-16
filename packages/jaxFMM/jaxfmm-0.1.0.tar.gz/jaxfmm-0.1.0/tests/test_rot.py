import pytest
from jaxfmm.rotation import *
import jaxfmm.fmm as fmm
import jax.numpy as jnp
from jax.scipy.spatial.transform import Rotation
import jaxfmm.debug_helpers as dbg

@pytest.mark.parametrize('unitcube, phi, theta', [((128, {}), 0.6, 1.9), ((128, {}), 4.4, 5.7)], indirect=["unitcube"])
def test_mpl_rot(unitcube, phi, theta): # TODO: remove the hierarchy, we do not really need it here...
    chrgs, hier = unitcube
    p, unqs, invs = hier["p"], hier["unqs"], hier["invs"]

    # polar matrix coeffs
    basemat = get_polar_rot_coeff(p,unqs,jnp.array([[theta]]))

    # initial mpls
    mpls_og = fmm.get_initial_mpls(hier["pts"][None,...], chrgs[None,...],hier["boxcenters"][0],hier["p"])

    mpls = rot_azimuth(mpls_og,jnp.array([[phi]]))
    mpls = rot_polar(basemat,invs,mpls)
    mpls_back = rot_polar(basemat,invs,mpls,True)
    mpls_back = rot_azimuth(mpls_back,jnp.array([[phi]]),True)

    spacerot = Rotation.from_euler('zy', jnp.array([-phi,-theta]))
    mpls_manualrot = fmm.get_initial_mpls(spacerot.apply(hier["pts"])[None,...], chrgs[None,...],hier["boxcenters"][0],p)

    assert jnp.allclose(mpls_og,mpls_back,rtol=1e-2,atol=1e-2)      # test inverse rotation
    assert jnp.allclose(mpls_manualrot,mpls,rtol=1e-2,atol=1e-2)    # test forward rotation

@pytest.mark.parametrize('unitcube, phi, theta', [((128, {}), 0.6, 1.9), ((128, {}), 4.4, 5.7)], indirect=["unitcube"])
def test_loc_rot(unitcube, phi, theta):
    chrgs, hier = unitcube
    p, unqs, invs = hier["p"], hier["unqs"], hier["invs"]
    exp_pos = jnp.array([-1.0,2.3,-1.12])

    # polar matrix coeffs
    basemat = get_polar_rot_coeff(p,unqs,jnp.array([[theta]]))

    # initial mpls
    locs_og = dbg.get_locs(hier["pts"][None,...], chrgs[None,...],exp_pos[None,...], p)

    locs = rot_azimuth(locs_og,jnp.array([[phi]]),False,True)
    locs = rot_polar(basemat,invs,locs,False,True)
    locs_back = rot_polar(basemat,invs,locs,True,True)
    locs_back = rot_azimuth(locs_back,jnp.array([[phi]]),True,True)

    spacerot = Rotation.from_euler('zy', jnp.array([-phi,-theta]))
    locs_manualrot = dbg.get_locs(spacerot.apply(hier["pts"])[None,...], chrgs[None,...],spacerot.apply(exp_pos)[None,:],p)

    assert jnp.allclose(locs_og,locs_back,rtol=1e-2,atol=1e-2)      # test inverse rotation
    assert jnp.allclose(locs_manualrot,locs,rtol=1e-2,atol=1e-2)    # test forward rotation