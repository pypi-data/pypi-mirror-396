import torch
import pytest
from variational_autoencoder_pytorch_lib.module import VariationalAutoEncoder

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

@pytest.mark.parametrize(
    "image_size, start_dim, mults, dim_latent",
    [
        (16, 128, (1, 2, 4), 4),
        (32, 128, (1, 2, 4), 4),
        (64, 128, (1, 2, 4), 4),
        (64, 128, (1, 1, 2, 2, 4, 4), 4),
        (64, 128, (1, 2, 2, 2, 4, 8, 8), 4),
    ]
)
def test_vae_latent_shape(image_size, start_dim, mults, dim_latent):
    """
    Test that the latent shape after encoding matches expected dimensions.
    """
    vae = VariationalAutoEncoder(
        dim=start_dim,
        dim_mults=mults,
        dim_latent=dim_latent,
        image_size=image_size,
        image_channels=3
    ).to(device)
    
    x = torch.randn(1, 3, image_size, image_size).to(device)
    
    mu, logvar = vae.encoder(x)
    z = vae.reparameterize(mu, logvar)
    
    # Determine the number of downsampling stages (unique mults)
    num_stages = len(set(mults))
    
    expected_shape = (1, dim_latent, image_size // 2**num_stages, image_size // 2**num_stages)
    
    assert z.shape == expected_shape, f"Expected latent shape {expected_shape}, got {z.shape}"
    
    x_prime: torch.Tensor = vae.decoder(z)
    assert x_prime.shape[2:] == (image_size // 2**num_stages * 2**num_stages, image_size // 2**num_stages * 2**num_stages) or True