import { Injectable } from '@nestjs/common';
import { CreateTeamDto } from './dto/create-team.dto';
import { UpdateTeamDto } from './dto/update-team.dto';
import { InjectRepository } from '@nestjs/typeorm';
import { Team } from './entities/team.entity';
import { Repository } from 'typeorm';

@Injectable()
export class TeamsService {
  constructor(
    @InjectRepository(Team)
    private readonly teamRepository: Repository<Team>,
  ) {}

  async create(createTeamDto: CreateTeamDto) {
    const team = this.teamRepository.create(createTeamDto);
    return await this.teamRepository.save(team);
  }

  async findAll(): Promise<Team[]> {
    return await this.teamRepository.find({
      relations: ['manager', 'users'],
    });
  }

// Get team with manager and users
async findone(id: number): Promise<Team | null> {
  return await this.teamRepository.findOne({
    where: { id },
    relations: ['manager', 'users'],
  });
}

  async findBy(query: object) {
    return await Team.findOne(query);
  }

  async update(id: number, updateTeamDto: UpdateTeamDto) {
    await Team.update({ id }, updateTeamDto);
    return await Team.findOneBy({ id });
  }

  async remove(id: number) {
    await Team.delete({ id });
    return { deleted: true };
  }
}
