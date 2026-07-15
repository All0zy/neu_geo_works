function lam_if = iono_free_lambda(f)
lam1 = f.c/f.f1;
lam2 = f.c/f.f2;
coef1 = f.f1^2 / (f.f1^2 - f.f2^2);
coef2 = -f.f2^2 / (f.f1^2 - f.f2^2);
lam_if = 1 / (coef1/lam1 + coef2/lam2);
end
