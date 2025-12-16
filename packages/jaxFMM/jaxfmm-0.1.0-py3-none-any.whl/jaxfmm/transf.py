import jax
import jax.numpy as jnp
from jaxfmm.rotation import get_polar_rot_coeff, rot_azimuth, rot_polar, cart_to_sph
from jax.scipy.special import factorial as fac
from jaxfmm.basis import mpl_idx, inv_mpl_idx

@jax.jit
def M2M(coeffs, oldboxdims, newboxdims, unqs, invs):
    p = invs[-1].shape[0]-1
    n_chi = oldboxdims.shape[0]//newboxdims.shape[0]
    coeffs = coeffs.reshape((coeffs.shape[0]//n_chi,n_chi,coeffs.shape[1]))
    oldboxdims = oldboxdims.reshape((-1,n_chi,3))
    sph = cart_to_sph(oldboxdims - newboxdims[:,None,:])

    ### get rotation matrix components all at once
    basemat = get_polar_rot_coeff(p,unqs,sph[...,1])

    ### rotate
    coeffs = rot_azimuth(coeffs, sph[...,2])
    coeffs = rot_polar(basemat,invs,coeffs)

    ### shift in the rotated system
    new_coeffs = coeffs.copy()
    for j in range(1,p+1):
        fact = (sph[...,0]**j) / fac(j)
        ms, ns = inv_mpl_idx(jnp.arange((p-j+1)**2))
        idxs = ms + ns + (ns+j)**2 + j
        new_coeffs = new_coeffs.at[...,idxs].add(fact[...,None] * coeffs[...,:mpl_idx(p-j,p-j)+1])

    ### rotate back
    coeffs = rot_polar(basemat,invs,new_coeffs,True)
    coeffs = rot_azimuth(coeffs, sph[...,2],True)

    return coeffs.sum(axis=1)

@jax.jit
def L2L(coeffs, oldboxdims, newboxdims, unqs, invs):
    p = invs[-1].shape[0]-1
    n_chi = newboxdims.shape[0]//oldboxdims.shape[0]
    coeffs = coeffs[:,None,:]
    newboxdims = newboxdims.reshape((-1,n_chi,3))
    sph = cart_to_sph(newboxdims - oldboxdims[:,None,:])

    ### get rotation matrix components all at once
    basemat = get_polar_rot_coeff(p,unqs,sph[...,1])

    ### rotate
    coeffs = rot_azimuth(coeffs, sph[...,2],False,True)
    coeffs = rot_polar(basemat,invs,coeffs,False,True)

    ### shift in the rotated system
    new_coeffs = coeffs.copy()
    for j in range(1,p+1):
        fact = (sph[...,0]**j) / fac(j)
        ms, ns = inv_mpl_idx(jnp.arange((p-j+1)**2))
        idxs = ms + ns + (ns+j)**2 + j
        new_coeffs = new_coeffs.at[...,:mpl_idx(p-j,p-j)+1].add(fact[...,None] * coeffs[...,idxs])

    ### rotate back
    coeffs = rot_polar(basemat,invs,new_coeffs,True,True)
    coeffs = rot_azimuth(coeffs, sph[...,2],True,True)

    return coeffs.reshape((-1,coeffs.shape[-1]))

@jax.jit
def M2L(boxcenters, eval_boxcenters, mpl_cnct, unqs, invs, coeffs, img_cnct = jnp.array([[]])):
    p = invs[-1].shape[0]-1

    if(img_cnct.shape[1] > 0):  # both pbc images and real boxes, shift appropriately
        n_boxs = boxcenters.shape[0]
        ids = mpl_cnct%n_boxs
        sph = cart_to_sph(eval_boxcenters[:,None,:] - boxcenters[ids] - img_cnct.at[mpl_cnct//n_boxs].get(mode="fill",fill_value=1.23456789))   # TODO: see below
        ids += ((mpl_cnct//n_boxs)//img_cnct.shape[0])*n_boxs   # edit ids such that the padding is out of bounds
    else:   # open boundary conditions
        ids = mpl_cnct
        sph = cart_to_sph(eval_boxcenters[:,None,:] - boxcenters.at[ids].get(mode="fill",fill_value=1.23456789))    # TODO: replace this workaround with a nan_to_num call?
    coeffs = coeffs.at[ids].get(mode="fill",fill_value=0)   # the fill value ensures that padding is ignored

    ### get rotation matrix components all at once
    basemat = get_polar_rot_coeff(p,unqs,sph[...,1])

    ### rotate
    coeffs = rot_azimuth(coeffs, sph[...,2])
    coeffs = rot_polar(basemat,invs,coeffs)

    ### carry out M2L transformation in the rotated system
    for j in range(p+1):
        ns = jnp.arange(j,p+1)
        pws = ns[:,None] + ns[None,:]
        fact = (-1)**(ns[:,None]+j) * fac(pws)[None,None,...] / ((sph[...,0,None,None])**((pws + 1)[None,None,...])) # NOTE: the factor (-1) in front probably originates from the sign of the shift vector...

        ### real update
        idxs = mpl_idx(j,ns)
        coeffs = coeffs.at[...,idxs].set((fact * coeffs[...,None,idxs]).sum(axis=-1))

        if(j>0):    # imag update
            idxs = mpl_idx(-j,ns)
            coeffs = coeffs.at[...,idxs].set(-(fact * coeffs[...,None,idxs]).sum(axis=-1))  # imag update - note the inverse sign!

    ### rotate back
    coeffs = rot_polar(basemat,invs,coeffs,True,True)
    coeffs = rot_azimuth(coeffs, sph[...,2],True,True)

    return coeffs.sum(axis=1)   # add (shifted) coeffs together