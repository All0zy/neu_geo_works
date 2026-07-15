function y = iono_free_comb(o1, o2, f)
a1 = f.f1^2 / (f.f1^2 - f.f2^2);
a2 = -f.f2^2 / (f.f1^2 - f.f2^2);
y = a1 * o1 + a2 * o2;
end
