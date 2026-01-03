import { Injectable } from '@nestjs/common';
import { CreateManagerDto } from './dto/create-manager.dto';
import { UpdateManagerDto } from './dto/update-manager.dto';
import { InjectRepository } from '@nestjs/typeorm';
import { Manager } from './entities/manager.entity';
import { Repository } from 'typeorm';

@Injectable()
export class ManagersService {
  constructor(
    @InjectRepository(Manager)
    private readonly managerRepository: Repository<Manager>,
  ) {}

  async create(createManagerDto: CreateManagerDto) {
    const manager = this.managerRepository.create(createManagerDto);
    return await this.managerRepository.save(manager);
  }

  async findAll(): Promise<Manager[]> {
    return await this.managerRepository.find({
      relations: ['teams', 'projects'],
    });
  }

  // Get manager with all teams and projects
  async findManagerWithRelations(id: number): Promise<Manager | null> {
    return await this.managerRepository.findOne({
      where: { id },
      relations: ['teams', 'projects'],
    });
  }

  async findOne(id: number): Promise<Manager | null> {
    const manager = await Manager.findOneBy({ id });
    return manager;
  }

  async findBy(query: any) {
    return await Manager.findOne(query);
  }

  async update(id: number, updateManagerDto: UpdateManagerDto) {
    await Manager.update({ id }, updateManagerDto);
    return await Manager.findOneBy({ id });
  }

  async remove(id: number) {
    await Manager.delete({ id });
    return { deleted: true };
  }
}
